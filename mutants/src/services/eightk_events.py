"""
8-K Material Event Signal — Massive Stocks API

Form 8-K current reports disclose material corporate events that must be
reported to the SEC within 4 business days. Categories with strong signal value:

  Item 1.01 — Material Definitive Agreement    (M&A, partnership) → +8 BUY
  Item 1.02 — Termination of Material Agreement → −6 SELL
  Item 2.01 — Completion of Acquisition/Disposition → directional
  Item 5.02 — Departure/Appointment of Directors/Officers (CEO change)
               CEO departure → −6 / CEO appointment → +3
  Item 8.01 — Other Events (share buyback, debt restructuring)
  Item 7.01 — Regulation FD (guidance, investor presentation) → ±4

Window: only process 8-Ks filed within the last 5 trading days.
Cache: 2 hours per ticker.
"""

import logging
import os
import time
from datetime import date, timedelta

import aiohttp
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.8k_events")

_cache: dict[str, dict] = {}
_TTL = 1800  # 30 minutes — 8-K material events are time-sensitive

_BASE = "https://api.polygon.io"

# Item number → (direction_pts, label, sentiment)
_ITEM_MAP = {
    "1.01": (+8, "Material Agreement (M&A/Partnership)", "pos"),
    "1.02": (-6, "Agreement Termination", "neg"),
    "2.01": (+6, "Acquisition/Disposition Completed", "pos"),
    "2.06": (-8, "Material Impairment", "neg"),
    "5.02": (0, "Executive Change", "neutral"),  # parsed separately
    "7.01": (+4, "Reg FD / Guidance / Presentation", "pos"),
    "8.01": (+3, "Other Material Event", "pos"),
}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__parse_ceo_signal__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__parse_ceo_signal__mutmut)
def _parse_ceo_signal(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_orig(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_1(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = None
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_2(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.upper()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_3(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = None
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_4(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(None)
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_5(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w not in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_6(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("XXresignXX", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_7(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("RESIGN", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_8(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "XXdepartXX", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_9(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "DEPART", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_10(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "XXterminatXX", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_11(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "TERMINAT", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_12(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "XXstep downXX", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_13(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "STEP DOWN", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_14(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "XXleavesXX"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_15(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "LEAVES"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_16(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = None
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_17(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(None)
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_18(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w not in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_19(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("XXappointXX", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_20(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("APPOINT", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_21(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "XXnamedXX", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_22(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "NAMED", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_23(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "XXelectXX", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_24(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "ELECT", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_25(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "XXhireXX", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_26(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "HIRE", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_27(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "XXjoinsXX"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_28(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "JOINS"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_29(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return +6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_30(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -7.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_31(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "XXCEO/CFO departure — management uncertainty signalXX"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_32(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "ceo/cfo departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_33(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO DEPARTURE — MANAGEMENT UNCERTAINTY SIGNAL"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_34(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return -3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_35(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +4.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_36(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "XXNew CEO/CFO appointed — leadership transition catalystXX"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_37(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "new ceo/cfo appointed — leadership transition catalyst"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_38(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "NEW CEO/CFO APPOINTED — LEADERSHIP TRANSITION CATALYST"
    return 0.0, ""


def x__parse_ceo_signal__mutmut_39(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 1.0, ""


def x__parse_ceo_signal__mutmut_40(text: str) -> tuple[float, str]:
    """Parse 5.02 item text for CEO/CFO appointment vs departure."""
    tl = text.lower()
    is_departure = any(w in tl for w in ("resign", "depart", "terminat", "step down", "leaves"))
    is_appoint = any(w in tl for w in ("appoint", "named", "elect", "hire", "joins"))
    if is_departure:
        return -6.0, "CEO/CFO departure — management uncertainty signal"
    if is_appoint:
        return +3.0, "New CEO/CFO appointed — leadership transition catalyst"
    return 0.0, "XXXX"

mutants_x__parse_ceo_signal__mutmut['_mutmut_orig'] = x__parse_ceo_signal__mutmut_orig # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_1'] = x__parse_ceo_signal__mutmut_1 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_2'] = x__parse_ceo_signal__mutmut_2 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_3'] = x__parse_ceo_signal__mutmut_3 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_4'] = x__parse_ceo_signal__mutmut_4 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_5'] = x__parse_ceo_signal__mutmut_5 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_6'] = x__parse_ceo_signal__mutmut_6 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_7'] = x__parse_ceo_signal__mutmut_7 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_8'] = x__parse_ceo_signal__mutmut_8 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_9'] = x__parse_ceo_signal__mutmut_9 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_10'] = x__parse_ceo_signal__mutmut_10 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_11'] = x__parse_ceo_signal__mutmut_11 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_12'] = x__parse_ceo_signal__mutmut_12 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_13'] = x__parse_ceo_signal__mutmut_13 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_14'] = x__parse_ceo_signal__mutmut_14 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_15'] = x__parse_ceo_signal__mutmut_15 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_16'] = x__parse_ceo_signal__mutmut_16 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_17'] = x__parse_ceo_signal__mutmut_17 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_18'] = x__parse_ceo_signal__mutmut_18 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_19'] = x__parse_ceo_signal__mutmut_19 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_20'] = x__parse_ceo_signal__mutmut_20 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_21'] = x__parse_ceo_signal__mutmut_21 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_22'] = x__parse_ceo_signal__mutmut_22 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_23'] = x__parse_ceo_signal__mutmut_23 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_24'] = x__parse_ceo_signal__mutmut_24 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_25'] = x__parse_ceo_signal__mutmut_25 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_26'] = x__parse_ceo_signal__mutmut_26 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_27'] = x__parse_ceo_signal__mutmut_27 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_28'] = x__parse_ceo_signal__mutmut_28 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_29'] = x__parse_ceo_signal__mutmut_29 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_30'] = x__parse_ceo_signal__mutmut_30 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_31'] = x__parse_ceo_signal__mutmut_31 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_32'] = x__parse_ceo_signal__mutmut_32 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_33'] = x__parse_ceo_signal__mutmut_33 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_34'] = x__parse_ceo_signal__mutmut_34 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_35'] = x__parse_ceo_signal__mutmut_35 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_36'] = x__parse_ceo_signal__mutmut_36 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_37'] = x__parse_ceo_signal__mutmut_37 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_38'] = x__parse_ceo_signal__mutmut_38 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_39'] = x__parse_ceo_signal__mutmut_39 # type: ignore # mutmut generated
mutants_x__parse_ceo_signal__mutmut['x__parse_ceo_signal__mutmut_40'] = x__parse_ceo_signal__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_8k_signals__mutmut)
async def get_8k_signals(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_orig(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_1(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = None
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_2(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache or now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_3(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker not in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_4(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now + _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_5(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["XXtsXX"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_6(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["TS"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_7(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] <= _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_8(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["XXdataXX"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_9(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["DATA"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_10(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = None
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_11(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv(None)
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_12(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("XXMASSIVE_API_KEYXX")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_13(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("massive_api_key")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_14(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_15(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"XXscoreXX": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_16(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"SCORE": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_17(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 1.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_18(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "XXeventsXX": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_19(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "EVENTS": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_20(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "XXfilingsXX": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_21(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "FILINGS": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_22(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = None
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_23(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = None
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_24(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() + timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_25(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=None)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_26(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=6)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_27(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = None
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_28(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = None

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_29(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"XXapiKeyXX": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_30(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apikey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_31(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"APIKEY": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_32(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "XXtickerXX": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_33(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "TICKER": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_34(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "XXtypeXX": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_35(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "TYPE": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_36(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "XX8-KXX", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_37(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-k", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_38(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "XXfiling_date.gteXX": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_39(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "FILING_DATE.GTE": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_40(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "XXlimitXX": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_41(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "LIMIT": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_42(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 6}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_43(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(None, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_44(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=None, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_45(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_46(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=None) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_47(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_48(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_49(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_50(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, ) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_51(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=None)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_52(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=9)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_53(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_54(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 201:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_55(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"XXscoreXX": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_56(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"SCORE": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_57(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 1.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_58(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "XXeventsXX": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_59(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "EVENTS": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_60(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "XXfilingsXX": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_61(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "FILINGS": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_62(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = None
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_63(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = None
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_64(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") and []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_65(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get(None) or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_66(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("XXresultsXX") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_67(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("RESULTS") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_68(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(None)
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_69(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"XXscoreXX": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_70(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"SCORE": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_71(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 1.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_72(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "XXeventsXX": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_73(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "EVENTS": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_74(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "XXfilingsXX": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_75(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "FILINGS": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_76(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = None
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_77(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 1.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_78(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = None
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_79(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = None

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_80(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = None
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_81(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") and []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_82(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get(None) or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_83(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("XXitemsXX") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_84(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("ITEMS") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_85(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = None
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_86(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") and ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_87(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") and filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_88(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get(None) or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_89(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("XXtextXX") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_90(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("TEXT") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_91(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get(None) or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_92(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("XXcontentXX") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_93(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("CONTENT") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_94(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or "XXXX"
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_95(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = None

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_96(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") and ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_97(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") and filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_98(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get(None) or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_99(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("XXfiled_atXX") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_100(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("FILED_AT") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_101(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get(None) or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_102(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("XXfiledXX") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_103(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("FILED") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_104(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or "XXXX"

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_105(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = None
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_106(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip(None).strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_107(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).rstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_108(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(None).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_109(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("XXItem XX").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_110(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_111(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("ITEM ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_112(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = None
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_113(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(None)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_114(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_115(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                break
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_116(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = None
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_117(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key != "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_118(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "XX5.02XX":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_119(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = None
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_120(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(None)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_121(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = None
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_122(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "XXnegXX" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_123(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "NEG" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_124(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts <= 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_125(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 1 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_126(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "XXposXX" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_127(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "POS" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_128(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts >= 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_129(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 1 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_130(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "XXneutralXX"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_131(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "NEUTRAL"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_132(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts == 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_133(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 1:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_134(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score = pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_135(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score -= pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_136(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(None)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_137(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    None
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_138(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "XXitemXX": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_139(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "ITEM": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_140(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "XXlabelXX": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_141(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "LABEL": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_142(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "XXscoreXX": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_143(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "SCORE": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_144(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "XXsentimentXX": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_145(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "SENTIMENT": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_146(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "XXfiledXX": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_147(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "FILED": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_148(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:11],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_149(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = None
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_150(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "XXscoreXX": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_151(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "SCORE": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_152(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(None, 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_153(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), None),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_154(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_155(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), ),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_156(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(None, 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_157(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), None), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_158(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_159(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), ), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_160(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(None, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_161(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, None), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_162(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(-12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_163(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, ), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_164(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, +12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_165(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -13.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_166(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 11.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_167(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 2),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_168(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "XXeventsXX": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_169(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "EVENTS": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_170(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "XXfilingsXX": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_171(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "FILINGS": parsed_filings,
    }
    _cache[ticker] = {"data": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_172(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = None
    return result


async def x_get_8k_signals__mutmut_173(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"XXdataXX": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_174(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"DATA": result, "ts": now}
    return result


async def x_get_8k_signals__mutmut_175(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "XXtsXX": now}
    return result


async def x_get_8k_signals__mutmut_176(ticker: str) -> dict:
    """
    Fetch recent 8-K filings for a ticker from Massive.
    Returns {"score": float, "events": list[str], "filings": list[dict]}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["data"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return {"score": 0.0, "events": [], "filings": []}

    ssl_ctx = get_ssl_context()
    cutoff = (date.today() - timedelta(days=5)).isoformat()
    url = f"{_BASE}/vX/reference/sec/filings"
    params = {"apiKey": api_key, "ticker": ticker, "type": "8-K", "filing_date.gte": cutoff, "limit": 5}

    try:
        async with shared_session() as session:
            async with session.get(url, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return {"score": 0.0, "events": [], "filings": []}
                data = await resp.json()
                filings = data.get("results") or []
    except Exception as e:
        log.debug(f"[8k] {ticker} fetch failed: {e}")
        return {"score": 0.0, "events": [], "filings": []}

    total_score = 0.0
    event_labels = []
    parsed_filings = []

    for filing in filings:
        items = filing.get("items") or []
        text = filing.get("text") or filing.get("content") or ""
        filed = filing.get("filed_at") or filing.get("filed") or ""

        for item_num in items:
            item_key = str(item_num).lstrip("Item ").strip()
            meta = _ITEM_MAP.get(item_key)
            if not meta:
                continue
            pts, label, sentiment = meta
            if item_key == "5.02":
                pts, label = _parse_ceo_signal(text)
                sentiment = "neg" if pts < 0 else "pos" if pts > 0 else "neutral"
            if pts != 0:
                total_score += pts
                event_labels.append(label)
                parsed_filings.append(
                    {
                        "item": item_key,
                        "label": label,
                        "score": pts,
                        "sentiment": sentiment,
                        "filed": filed[:10],
                    }
                )

    result = {
        "score": round(min(max(total_score, -12.0), 10.0), 1),
        "events": event_labels,
        "filings": parsed_filings,
    }
    _cache[ticker] = {"data": result, "TS": now}
    return result

mutants_x_get_8k_signals__mutmut['_mutmut_orig'] = x_get_8k_signals__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_1'] = x_get_8k_signals__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_2'] = x_get_8k_signals__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_3'] = x_get_8k_signals__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_4'] = x_get_8k_signals__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_5'] = x_get_8k_signals__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_6'] = x_get_8k_signals__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_7'] = x_get_8k_signals__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_8'] = x_get_8k_signals__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_9'] = x_get_8k_signals__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_10'] = x_get_8k_signals__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_11'] = x_get_8k_signals__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_12'] = x_get_8k_signals__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_13'] = x_get_8k_signals__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_14'] = x_get_8k_signals__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_15'] = x_get_8k_signals__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_16'] = x_get_8k_signals__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_17'] = x_get_8k_signals__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_18'] = x_get_8k_signals__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_19'] = x_get_8k_signals__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_20'] = x_get_8k_signals__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_21'] = x_get_8k_signals__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_22'] = x_get_8k_signals__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_23'] = x_get_8k_signals__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_24'] = x_get_8k_signals__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_25'] = x_get_8k_signals__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_26'] = x_get_8k_signals__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_27'] = x_get_8k_signals__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_28'] = x_get_8k_signals__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_29'] = x_get_8k_signals__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_30'] = x_get_8k_signals__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_31'] = x_get_8k_signals__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_32'] = x_get_8k_signals__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_33'] = x_get_8k_signals__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_34'] = x_get_8k_signals__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_35'] = x_get_8k_signals__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_36'] = x_get_8k_signals__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_37'] = x_get_8k_signals__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_38'] = x_get_8k_signals__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_39'] = x_get_8k_signals__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_40'] = x_get_8k_signals__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_41'] = x_get_8k_signals__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_42'] = x_get_8k_signals__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_43'] = x_get_8k_signals__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_44'] = x_get_8k_signals__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_45'] = x_get_8k_signals__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_46'] = x_get_8k_signals__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_47'] = x_get_8k_signals__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_48'] = x_get_8k_signals__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_49'] = x_get_8k_signals__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_50'] = x_get_8k_signals__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_51'] = x_get_8k_signals__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_52'] = x_get_8k_signals__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_53'] = x_get_8k_signals__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_54'] = x_get_8k_signals__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_55'] = x_get_8k_signals__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_56'] = x_get_8k_signals__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_57'] = x_get_8k_signals__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_58'] = x_get_8k_signals__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_59'] = x_get_8k_signals__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_60'] = x_get_8k_signals__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_61'] = x_get_8k_signals__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_62'] = x_get_8k_signals__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_63'] = x_get_8k_signals__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_64'] = x_get_8k_signals__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_65'] = x_get_8k_signals__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_66'] = x_get_8k_signals__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_67'] = x_get_8k_signals__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_68'] = x_get_8k_signals__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_69'] = x_get_8k_signals__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_70'] = x_get_8k_signals__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_71'] = x_get_8k_signals__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_72'] = x_get_8k_signals__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_73'] = x_get_8k_signals__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_74'] = x_get_8k_signals__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_75'] = x_get_8k_signals__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_76'] = x_get_8k_signals__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_77'] = x_get_8k_signals__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_78'] = x_get_8k_signals__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_79'] = x_get_8k_signals__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_80'] = x_get_8k_signals__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_81'] = x_get_8k_signals__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_82'] = x_get_8k_signals__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_83'] = x_get_8k_signals__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_84'] = x_get_8k_signals__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_85'] = x_get_8k_signals__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_86'] = x_get_8k_signals__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_87'] = x_get_8k_signals__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_88'] = x_get_8k_signals__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_89'] = x_get_8k_signals__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_90'] = x_get_8k_signals__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_91'] = x_get_8k_signals__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_92'] = x_get_8k_signals__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_93'] = x_get_8k_signals__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_94'] = x_get_8k_signals__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_95'] = x_get_8k_signals__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_96'] = x_get_8k_signals__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_97'] = x_get_8k_signals__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_98'] = x_get_8k_signals__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_99'] = x_get_8k_signals__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_100'] = x_get_8k_signals__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_101'] = x_get_8k_signals__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_102'] = x_get_8k_signals__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_103'] = x_get_8k_signals__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_104'] = x_get_8k_signals__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_105'] = x_get_8k_signals__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_106'] = x_get_8k_signals__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_107'] = x_get_8k_signals__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_108'] = x_get_8k_signals__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_109'] = x_get_8k_signals__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_110'] = x_get_8k_signals__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_111'] = x_get_8k_signals__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_112'] = x_get_8k_signals__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_113'] = x_get_8k_signals__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_114'] = x_get_8k_signals__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_115'] = x_get_8k_signals__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_116'] = x_get_8k_signals__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_117'] = x_get_8k_signals__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_118'] = x_get_8k_signals__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_119'] = x_get_8k_signals__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_120'] = x_get_8k_signals__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_121'] = x_get_8k_signals__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_122'] = x_get_8k_signals__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_123'] = x_get_8k_signals__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_124'] = x_get_8k_signals__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_125'] = x_get_8k_signals__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_126'] = x_get_8k_signals__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_127'] = x_get_8k_signals__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_128'] = x_get_8k_signals__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_129'] = x_get_8k_signals__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_130'] = x_get_8k_signals__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_131'] = x_get_8k_signals__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_132'] = x_get_8k_signals__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_133'] = x_get_8k_signals__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_134'] = x_get_8k_signals__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_135'] = x_get_8k_signals__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_136'] = x_get_8k_signals__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_137'] = x_get_8k_signals__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_138'] = x_get_8k_signals__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_139'] = x_get_8k_signals__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_140'] = x_get_8k_signals__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_141'] = x_get_8k_signals__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_142'] = x_get_8k_signals__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_143'] = x_get_8k_signals__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_144'] = x_get_8k_signals__mutmut_144 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_145'] = x_get_8k_signals__mutmut_145 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_146'] = x_get_8k_signals__mutmut_146 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_147'] = x_get_8k_signals__mutmut_147 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_148'] = x_get_8k_signals__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_149'] = x_get_8k_signals__mutmut_149 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_150'] = x_get_8k_signals__mutmut_150 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_151'] = x_get_8k_signals__mutmut_151 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_152'] = x_get_8k_signals__mutmut_152 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_153'] = x_get_8k_signals__mutmut_153 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_154'] = x_get_8k_signals__mutmut_154 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_155'] = x_get_8k_signals__mutmut_155 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_156'] = x_get_8k_signals__mutmut_156 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_157'] = x_get_8k_signals__mutmut_157 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_158'] = x_get_8k_signals__mutmut_158 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_159'] = x_get_8k_signals__mutmut_159 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_160'] = x_get_8k_signals__mutmut_160 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_161'] = x_get_8k_signals__mutmut_161 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_162'] = x_get_8k_signals__mutmut_162 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_163'] = x_get_8k_signals__mutmut_163 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_164'] = x_get_8k_signals__mutmut_164 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_165'] = x_get_8k_signals__mutmut_165 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_166'] = x_get_8k_signals__mutmut_166 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_167'] = x_get_8k_signals__mutmut_167 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_168'] = x_get_8k_signals__mutmut_168 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_169'] = x_get_8k_signals__mutmut_169 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_170'] = x_get_8k_signals__mutmut_170 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_171'] = x_get_8k_signals__mutmut_171 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_172'] = x_get_8k_signals__mutmut_172 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_173'] = x_get_8k_signals__mutmut_173 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_174'] = x_get_8k_signals__mutmut_174 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_175'] = x_get_8k_signals__mutmut_175 # type: ignore # mutmut generated
mutants_x_get_8k_signals__mutmut['x_get_8k_signals__mutmut_176'] = x_get_8k_signals__mutmut_176 # type: ignore # mutmut generated
