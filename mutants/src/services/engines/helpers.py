"""Leaf helpers and shared constants for the signal engine (BE-1 refactor).

Extracted verbatim from ``signal_engine.py``. This module has no dependency on
``signal_engine`` (leaf of the import DAG): ``signal_engine`` and
``engines/assembler.py`` both import from here.
"""

from datetime import datetime
from datetime import time as dtime

import pytz

_ET = pytz.timezone("America/New_York")


# ── Per-sector MR calibration (alpha-decomp §13-§15 findings) ────────────────
# Keys: sector ETF symbol (from services.sector.SECTOR_MAP).
# vix_min:      minimum VIX at MR entry (§15c). None = no floor.
# hold_days:    recommended hold period for MR bounces (§15b).
# atr_rank_min: minimum ATR%rank for MR entries (§15e). 20 = global default.
# buy_thresh:   minimum composite score for MR BUY signals (§15d). None = global 35.
# Sectors with None calibration = pending §16 research; global defaults apply.
#
# CURVE-FIT WARNING: per-sector thresholds (vix_min, buy_thresh, atr_rank_min)
# are tuned on N=4–24 tickers per sector.  These parameters likely over-fit
# in-sample; treat sector-specific values as soft priors, not hard truths.
# Validate via OOS walk-forward before tightening further.  The global ATR≥20
# gate is the most robust signal; sector-specific overlays add marginal lift.
_SECTOR_MR_CONFIG: dict[str, dict] = {
    # ── Active sectors — global buy_thresh and vix_min (de-curated per audit) ────
    # Per-sector buy_thresh and vix_min were tuned on N=4–24 tickers (§15-§16).
    # Walk-forward OOS (§19/§20/§35a): strict per-sector params passed 1/5 windows;
    # global/relaxed params passed 2/5. Over-curated params destroyed OOS survival.
    # FIX: remove per-sector buy_thresh and vix_min. Keep only structurally-proven
    # gates: atr_rank_min (ATR≥20 is robust across all regimes) and hold_days
    # (already deployed in live recommendedHoldDays — low-harm to leave).
    "XLK": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Tech/FAANG
    "XLF": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 30,
        "buy_thresh": None,
    },  # Financials (blocked by delivery_gates XLF floor anyway)
    "XLY": {"vix_min": None, "hold_days": 10, "atr_rank_min": 20, "buy_thresh": None},  # Consumer Disc
    "XLP": {
        "vix_min": None,
        "hold_days": 10,
        "atr_rank_min": 20,
        "buy_thresh": None,
    },  # Consumer Staples (blocked by delivery_gates)
    "XLE": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Energy
    "XLC": {"vix_min": None, "hold_days": 10, "atr_rank_min": 20, "buy_thresh": None},  # Telecom/Comm
    "XLB": {"vix_min": None, "hold_days": 5, "atr_rank_min": 20, "buy_thresh": None},  # Materials
    "XLU": {
        "vix_min": None,
        "hold_days": 10,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Utilities — no viable MR edge; blocked
    # ── §16 confirmed-negative sectors — buy_thresh=999 blocks all MR entries ────
    "XLV": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 30,
        "buy_thresh": 999,
    },  # Healthcare — §16a Sharpe −0.17; blocked
    "XLI": {
        "vix_min": None,
        "hold_days": 7,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Industrials — §16a Sharpe −0.48; blocked
    "XLRE": {
        "vix_min": None,
        "hold_days": 5,
        "atr_rank_min": 20,
        "buy_thresh": 999,
    },  # Real Estate — §16a Sharpe −15; blocked
}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__current_session__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__current_session__mutmut)
def _current_session() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_orig() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_1() -> str:
    t = None
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_2() -> str:
    t = datetime.now(None).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_3() -> str:
    t = datetime.now(_ET).time()
    if dtime(None, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_4() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, None) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_5() -> str:
    t = datetime.now(_ET).time()
    if dtime(0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_6() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, ) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_7() -> str:
    t = datetime.now(_ET).time()
    if dtime(5, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_8() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 1) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_9() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) < t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_10() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t <= dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_11() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(None, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_12() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, None):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_13() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_14() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, ):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_15() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(10, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_16() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 31):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_17() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "XXpreXX"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_18() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "PRE"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_19() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(None, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_20() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, None) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_21() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_22() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, ) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_23() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(10, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_24() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 31) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_25() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) < t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_26() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t <= dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_27() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(None, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_28() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, None):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_29() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_30() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, ):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_31() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(17, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_32() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 1):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_33() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "XXregularXX"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_34() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "REGULAR"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_35() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(None, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_36() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, None) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_37() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_38() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, ) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_39() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(17, 0) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_40() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 1) <= t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_41() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) < t < dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_42() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t <= dtime(20, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_43() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(None, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_44() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, None):
        return "after"
    return "closed"


def x__current_session__mutmut_45() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(0):
        return "after"
    return "closed"


def x__current_session__mutmut_46() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, ):
        return "after"
    return "closed"


def x__current_session__mutmut_47() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(21, 0):
        return "after"
    return "closed"


def x__current_session__mutmut_48() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 1):
        return "after"
    return "closed"


def x__current_session__mutmut_49() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "XXafterXX"
    return "closed"


def x__current_session__mutmut_50() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "AFTER"
    return "closed"


def x__current_session__mutmut_51() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "XXclosedXX"


def x__current_session__mutmut_52() -> str:
    t = datetime.now(_ET).time()
    if dtime(4, 0) <= t < dtime(9, 30):
        return "pre"
    if dtime(9, 30) <= t < dtime(16, 0):
        return "regular"
    if dtime(16, 0) <= t < dtime(20, 0):
        return "after"
    return "CLOSED"

mutants_x__current_session__mutmut['_mutmut_orig'] = x__current_session__mutmut_orig # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_1'] = x__current_session__mutmut_1 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_2'] = x__current_session__mutmut_2 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_3'] = x__current_session__mutmut_3 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_4'] = x__current_session__mutmut_4 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_5'] = x__current_session__mutmut_5 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_6'] = x__current_session__mutmut_6 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_7'] = x__current_session__mutmut_7 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_8'] = x__current_session__mutmut_8 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_9'] = x__current_session__mutmut_9 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_10'] = x__current_session__mutmut_10 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_11'] = x__current_session__mutmut_11 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_12'] = x__current_session__mutmut_12 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_13'] = x__current_session__mutmut_13 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_14'] = x__current_session__mutmut_14 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_15'] = x__current_session__mutmut_15 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_16'] = x__current_session__mutmut_16 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_17'] = x__current_session__mutmut_17 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_18'] = x__current_session__mutmut_18 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_19'] = x__current_session__mutmut_19 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_20'] = x__current_session__mutmut_20 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_21'] = x__current_session__mutmut_21 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_22'] = x__current_session__mutmut_22 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_23'] = x__current_session__mutmut_23 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_24'] = x__current_session__mutmut_24 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_25'] = x__current_session__mutmut_25 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_26'] = x__current_session__mutmut_26 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_27'] = x__current_session__mutmut_27 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_28'] = x__current_session__mutmut_28 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_29'] = x__current_session__mutmut_29 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_30'] = x__current_session__mutmut_30 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_31'] = x__current_session__mutmut_31 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_32'] = x__current_session__mutmut_32 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_33'] = x__current_session__mutmut_33 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_34'] = x__current_session__mutmut_34 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_35'] = x__current_session__mutmut_35 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_36'] = x__current_session__mutmut_36 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_37'] = x__current_session__mutmut_37 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_38'] = x__current_session__mutmut_38 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_39'] = x__current_session__mutmut_39 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_40'] = x__current_session__mutmut_40 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_41'] = x__current_session__mutmut_41 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_42'] = x__current_session__mutmut_42 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_43'] = x__current_session__mutmut_43 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_44'] = x__current_session__mutmut_44 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_45'] = x__current_session__mutmut_45 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_46'] = x__current_session__mutmut_46 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_47'] = x__current_session__mutmut_47 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_48'] = x__current_session__mutmut_48 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_49'] = x__current_session__mutmut_49 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_50'] = x__current_session__mutmut_50 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_51'] = x__current_session__mutmut_51 # type: ignore # mutmut generated
mutants_x__current_session__mutmut['x__current_session__mutmut_52'] = x__current_session__mutmut_52 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__score_to_action__mutmut)
def _score_to_action(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_orig(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_1(score: float, agreement: int = 1) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_2(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = None
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_3(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(None)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_4(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = None
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_5(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(None, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_6(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, None)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_7(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_8(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, )
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_9(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(3.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_10(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement / 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_11(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 1.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_12(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = None
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_13(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) - agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_14(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 - 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_15(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 36.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_16(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 / (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_17(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 51.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_18(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 + math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_19(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (2.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_20(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(None)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_21(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s * 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_22(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(+abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_23(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 81.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_24(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = None
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_25(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(None, 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_26(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), None)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_27(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_28(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), )
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_29(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(None, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_30(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, None), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_31(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_32(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, ), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_33(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(79.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_34(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 2)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_35(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score > 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_36(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 36:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_37(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "XXBUYXX", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_38(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "buy", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_39(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score < -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_40(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= +30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_41(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -31:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_42(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "XXSELLXX", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_43(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "sell", confidence
    return "HOLD", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_44(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "XXHOLDXX", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_45(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "hold", max(38.0, min(52.0, confidence))


def x__score_to_action__mutmut_46(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(None, min(52.0, confidence))


def x__score_to_action__mutmut_47(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, None)


def x__score_to_action__mutmut_48(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(min(52.0, confidence))


def x__score_to_action__mutmut_49(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, )


def x__score_to_action__mutmut_50(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(39.0, min(52.0, confidence))


def x__score_to_action__mutmut_51(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(None, confidence))


def x__score_to_action__mutmut_52(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, None))


def x__score_to_action__mutmut_53(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(confidence))


def x__score_to_action__mutmut_54(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(52.0, ))


def x__score_to_action__mutmut_55(score: float, agreement: int = 0) -> tuple[str, float]:
    """
    Map raw signal score → (action, raw_confidence).

    This produces the ALPHA SCORE component — used for trade ranking.
    The PROBABILITY component is produced by apply_calibration() in calibration.py.

    v2 change (calibration-v2 paper): wider sigmoid spread so the calibration
    layer has room to differentiate signal quality. The old 65% hard ceiling
    compressed score 35→100+ into a 7pp range (58–65%), making Brier ≈ random.

    New spread: score 35→50%, score 70→63%, score 100→70%, score 150→76%.
    The calibration ceiling (78%) is now enforced inside apply_calibration(),
    not here — this function is the alpha score, not the final confidence number.
    """
    import math

    abs_s = abs(score)
    # Wider sigmoid: 50% at score=35, 70% at score=100, 76% at score=150
    # Calibration then maps this to the empirical win rate for each band.
    agreement_bonus = min(2.0, agreement * 0.25)
    raw = 35.0 + 50.0 * (1.0 - math.exp(-abs_s / 80.0)) + agreement_bonus
    # Pre-calibration ceiling: 78% (same as calibration._CONF_CEIL)
    # This prevents the alpha score from starting outside the calibration's output range.
    confidence = round(min(78.0, raw), 1)
    # Thresholds are asymmetric: the system has a structural bullish bias (~+13 pts).
    # Raising BUY bar to 35 and SELL bar to -30 corrects for this.
    if score >= 35:
        return "BUY", confidence
    if score <= -30:
        return "SELL", confidence
    return "HOLD", max(38.0, min(53.0, confidence))

mutants_x__score_to_action__mutmut['_mutmut_orig'] = x__score_to_action__mutmut_orig # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_1'] = x__score_to_action__mutmut_1 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_2'] = x__score_to_action__mutmut_2 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_3'] = x__score_to_action__mutmut_3 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_4'] = x__score_to_action__mutmut_4 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_5'] = x__score_to_action__mutmut_5 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_6'] = x__score_to_action__mutmut_6 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_7'] = x__score_to_action__mutmut_7 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_8'] = x__score_to_action__mutmut_8 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_9'] = x__score_to_action__mutmut_9 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_10'] = x__score_to_action__mutmut_10 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_11'] = x__score_to_action__mutmut_11 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_12'] = x__score_to_action__mutmut_12 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_13'] = x__score_to_action__mutmut_13 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_14'] = x__score_to_action__mutmut_14 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_15'] = x__score_to_action__mutmut_15 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_16'] = x__score_to_action__mutmut_16 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_17'] = x__score_to_action__mutmut_17 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_18'] = x__score_to_action__mutmut_18 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_19'] = x__score_to_action__mutmut_19 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_20'] = x__score_to_action__mutmut_20 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_21'] = x__score_to_action__mutmut_21 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_22'] = x__score_to_action__mutmut_22 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_23'] = x__score_to_action__mutmut_23 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_24'] = x__score_to_action__mutmut_24 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_25'] = x__score_to_action__mutmut_25 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_26'] = x__score_to_action__mutmut_26 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_27'] = x__score_to_action__mutmut_27 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_28'] = x__score_to_action__mutmut_28 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_29'] = x__score_to_action__mutmut_29 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_30'] = x__score_to_action__mutmut_30 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_31'] = x__score_to_action__mutmut_31 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_32'] = x__score_to_action__mutmut_32 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_33'] = x__score_to_action__mutmut_33 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_34'] = x__score_to_action__mutmut_34 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_35'] = x__score_to_action__mutmut_35 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_36'] = x__score_to_action__mutmut_36 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_37'] = x__score_to_action__mutmut_37 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_38'] = x__score_to_action__mutmut_38 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_39'] = x__score_to_action__mutmut_39 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_40'] = x__score_to_action__mutmut_40 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_41'] = x__score_to_action__mutmut_41 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_42'] = x__score_to_action__mutmut_42 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_43'] = x__score_to_action__mutmut_43 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_44'] = x__score_to_action__mutmut_44 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_45'] = x__score_to_action__mutmut_45 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_46'] = x__score_to_action__mutmut_46 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_47'] = x__score_to_action__mutmut_47 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_48'] = x__score_to_action__mutmut_48 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_49'] = x__score_to_action__mutmut_49 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_50'] = x__score_to_action__mutmut_50 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_51'] = x__score_to_action__mutmut_51 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_52'] = x__score_to_action__mutmut_52 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_53'] = x__score_to_action__mutmut_53 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_54'] = x__score_to_action__mutmut_54 # type: ignore # mutmut generated
mutants_x__score_to_action__mutmut['x__score_to_action__mutmut_55'] = x__score_to_action__mutmut_55 # type: ignore # mutmut generated
mutants_x__levels__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__levels__mutmut)
def _levels(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_orig(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_1(price: float, atr: float, action: str, style: str = "XXswingXX", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_2(price: float, atr: float, action: str, style: str = "SWING", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_3(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" and atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_4(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action != "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_5(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "XXHOLDXX" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_6(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "hold" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_7(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr != 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_8(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 1:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_9(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "XX—XX"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_10(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = None
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_11(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = None

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_12(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr * price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_13(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price >= 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_14(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 1 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_15(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 1.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_16(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style != "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_17(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "XXpositionXX":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_18(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "POSITION":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_19(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct >= 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_20(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 1.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_21(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = None
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_22(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 3.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_23(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 4.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_24(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct <= 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_25(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 1.01:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_26(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = None
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_27(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 4.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_28(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 6.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_29(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = None
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_30(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 4.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_31(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 5.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_32(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style != "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_33(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "XXintradayXX":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_34(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "INTRADAY":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_35(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = None  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_36(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 2.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_37(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 3.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_38(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = None  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_39(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 2.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_40(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 3.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_41(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" or rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_42(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action != "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_43(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "XXBUYXX" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_44(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "buy" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_45(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_46(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi <= 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_47(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 31:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_48(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = None
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_49(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 3.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_50(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi <= 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_51(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 36:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_52(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = None

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_53(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 2.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_54(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = None
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_55(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(None, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_56(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, None) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_57(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_58(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, ) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_59(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry + stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_60(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult / atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_61(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 3) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_62(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action != "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_63(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "XXBUYXX" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_64(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "buy" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_65(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(None, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_66(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, None)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_67(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_68(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, )
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_69(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry - stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_70(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult / atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_71(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 3)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_72(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = None
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_73(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(None, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_74(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, None) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_75(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_76(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, ) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_77(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry - tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_78(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult / atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_79(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 3) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_80(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action != "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_81(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "XXBUYXX" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_82(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "buy" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_83(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(None, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_84(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, None)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_85(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_86(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, )
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_87(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry + tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_88(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult / atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_89(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 3)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_90(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = None
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_91(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(None)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_92(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry + stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_93(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = None
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_94(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(None)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_95(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target + entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_96(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = None
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_97(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward * risk:.1f}" if risk > 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_98(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk >= 0 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_99(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 1 else "—"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_100(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "XX—XX"
    return round(entry, 2), stop, target, rr


def x__levels__mutmut_101(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(None, 2), stop, target, rr


def x__levels__mutmut_102(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, None), stop, target, rr


def x__levels__mutmut_103(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(2), stop, target, rr


def x__levels__mutmut_104(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, ), stop, target, rr


def x__levels__mutmut_105(price: float, atr: float, action: str, style: str = "swing", rsi: float | None = None):
    if action == "HOLD" or atr == 0:
        return None, None, None, "—"
    entry = price
    atr_pct = atr / price if price > 0 else 0.02

    # Stop multipliers are style-specific.
    # §31 live data (543 resolved signals): swing stop-hit rate 44.9% at old 1.5×ATR stops.
    # Avg MFE/MAE=1.74× — direction is right but intraday noise was clipping stops.
    # Widened swing to 2.0×/2.5× (R:R≈1.25). Position trades unchanged (already 2.5-3.5×).
    if style == "position":
        if atr_pct > 0.025:  # high vol
            stop_mult, tgt_mult = 2.5, 3.5
        elif atr_pct < 0.010:  # low vol
            stop_mult, tgt_mult = 3.5, 5.0
        else:  # normal vol
            stop_mult, tgt_mult = 3.0, 4.5
    elif style == "intraday":
        stop_mult, tgt_mult = 1.0, 2.0  # tight — short hold time
    else:  # swing
        # §17 IS sensitivity (72-ticker 23yr): 1.5s/2.0t (all ATR cases) → Sharpe 0.29
        # vs 0.26 baseline adaptive (+0.03, +5.6pp WR, lower MaxDD). 1.0s/2.0t forced = 0.23.
        # Universal 1.5s/2.0t wins — consistent with §31 live finding (44.9% stop-hit at 1.5×,
        # indicating intraday wicks clip 1.0× stops before direction change materialises).
        stop_mult, tgt_mult = 1.5, 2.0  # universal 1.5s/2.0t — R:R 1.33
        # Dynamic stop widening for oversold entries (backtest-validated 2026-06-09).
        # RSI<30 → 2.0× ATR (wider stop before reversal bounce).
        # RSI<35 → 1.75× ATR (moderate widening).
        if action == "BUY" and rsi is not None:
            if rsi < 30:
                stop_mult = 2.0
            elif rsi < 35:
                stop_mult = 1.75

    stop = round(entry - stop_mult * atr, 2) if action == "BUY" else round(entry + stop_mult * atr, 2)
    target = round(entry + tgt_mult * atr, 2) if action == "BUY" else round(entry - tgt_mult * atr, 2)
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr = f"{reward / risk:.1f}" if risk > 0 else "—"
    return round(entry, 3), stop, target, rr

mutants_x__levels__mutmut['_mutmut_orig'] = x__levels__mutmut_orig # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_1'] = x__levels__mutmut_1 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_2'] = x__levels__mutmut_2 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_3'] = x__levels__mutmut_3 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_4'] = x__levels__mutmut_4 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_5'] = x__levels__mutmut_5 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_6'] = x__levels__mutmut_6 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_7'] = x__levels__mutmut_7 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_8'] = x__levels__mutmut_8 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_9'] = x__levels__mutmut_9 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_10'] = x__levels__mutmut_10 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_11'] = x__levels__mutmut_11 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_12'] = x__levels__mutmut_12 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_13'] = x__levels__mutmut_13 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_14'] = x__levels__mutmut_14 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_15'] = x__levels__mutmut_15 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_16'] = x__levels__mutmut_16 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_17'] = x__levels__mutmut_17 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_18'] = x__levels__mutmut_18 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_19'] = x__levels__mutmut_19 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_20'] = x__levels__mutmut_20 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_21'] = x__levels__mutmut_21 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_22'] = x__levels__mutmut_22 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_23'] = x__levels__mutmut_23 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_24'] = x__levels__mutmut_24 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_25'] = x__levels__mutmut_25 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_26'] = x__levels__mutmut_26 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_27'] = x__levels__mutmut_27 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_28'] = x__levels__mutmut_28 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_29'] = x__levels__mutmut_29 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_30'] = x__levels__mutmut_30 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_31'] = x__levels__mutmut_31 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_32'] = x__levels__mutmut_32 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_33'] = x__levels__mutmut_33 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_34'] = x__levels__mutmut_34 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_35'] = x__levels__mutmut_35 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_36'] = x__levels__mutmut_36 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_37'] = x__levels__mutmut_37 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_38'] = x__levels__mutmut_38 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_39'] = x__levels__mutmut_39 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_40'] = x__levels__mutmut_40 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_41'] = x__levels__mutmut_41 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_42'] = x__levels__mutmut_42 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_43'] = x__levels__mutmut_43 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_44'] = x__levels__mutmut_44 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_45'] = x__levels__mutmut_45 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_46'] = x__levels__mutmut_46 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_47'] = x__levels__mutmut_47 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_48'] = x__levels__mutmut_48 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_49'] = x__levels__mutmut_49 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_50'] = x__levels__mutmut_50 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_51'] = x__levels__mutmut_51 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_52'] = x__levels__mutmut_52 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_53'] = x__levels__mutmut_53 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_54'] = x__levels__mutmut_54 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_55'] = x__levels__mutmut_55 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_56'] = x__levels__mutmut_56 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_57'] = x__levels__mutmut_57 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_58'] = x__levels__mutmut_58 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_59'] = x__levels__mutmut_59 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_60'] = x__levels__mutmut_60 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_61'] = x__levels__mutmut_61 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_62'] = x__levels__mutmut_62 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_63'] = x__levels__mutmut_63 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_64'] = x__levels__mutmut_64 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_65'] = x__levels__mutmut_65 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_66'] = x__levels__mutmut_66 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_67'] = x__levels__mutmut_67 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_68'] = x__levels__mutmut_68 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_69'] = x__levels__mutmut_69 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_70'] = x__levels__mutmut_70 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_71'] = x__levels__mutmut_71 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_72'] = x__levels__mutmut_72 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_73'] = x__levels__mutmut_73 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_74'] = x__levels__mutmut_74 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_75'] = x__levels__mutmut_75 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_76'] = x__levels__mutmut_76 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_77'] = x__levels__mutmut_77 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_78'] = x__levels__mutmut_78 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_79'] = x__levels__mutmut_79 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_80'] = x__levels__mutmut_80 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_81'] = x__levels__mutmut_81 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_82'] = x__levels__mutmut_82 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_83'] = x__levels__mutmut_83 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_84'] = x__levels__mutmut_84 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_85'] = x__levels__mutmut_85 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_86'] = x__levels__mutmut_86 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_87'] = x__levels__mutmut_87 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_88'] = x__levels__mutmut_88 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_89'] = x__levels__mutmut_89 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_90'] = x__levels__mutmut_90 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_91'] = x__levels__mutmut_91 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_92'] = x__levels__mutmut_92 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_93'] = x__levels__mutmut_93 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_94'] = x__levels__mutmut_94 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_95'] = x__levels__mutmut_95 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_96'] = x__levels__mutmut_96 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_97'] = x__levels__mutmut_97 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_98'] = x__levels__mutmut_98 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_99'] = x__levels__mutmut_99 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_100'] = x__levels__mutmut_100 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_101'] = x__levels__mutmut_101 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_102'] = x__levels__mutmut_102 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_103'] = x__levels__mutmut_103 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_104'] = x__levels__mutmut_104 # type: ignore # mutmut generated
mutants_x__levels__mutmut['x__levels__mutmut_105'] = x__levels__mutmut_105 # type: ignore # mutmut generated


_TIMEFRAME = {
    "intraday": ("within today's session (next few hours)", "Today"),
    "swing": ("over the next 2–10 trading days", "2–10 days"),
    "position": ("over the coming weeks to months", "Weeks–months"),
}

# Leveraged and inverse-leveraged ETFs. Scoring blocks that rely on company
# fundamentals (Piotroski, FCF, earnings, insider Form 4, analyst EPS revisions,
# 13F) are bypassed for these tickers because those signals don't apply to
# daily-rebalancing derivative products. Technical and macro signals still run.
# Style is capped at "swing" — holding beyond ~5 days incurs significant
# volatility-decay drag that makes position-style targets unreliable.
_LEVERAGED_ETFS: frozenset[str] = frozenset(
    {
        # ── 3× Bull ──────────────────────────────────────────────────────────────
        "TQQQ",  # ProShares UltraPro QQQ
        "UPRO",  # ProShares UltraPro S&P 500
        "SPXL",  # Direxion Daily S&P 500 Bull 3×
        "SOXL",  # Direxion Daily Semiconductor Bull 3×
        "TECL",  # Direxion Daily Technology Bull 3×
        "FAS",  # Direxion Daily Financial Bull 3×
        "TNA",  # Direxion Daily Small Cap Bull 3×
        "LABU",  # Direxion Daily S&P Biotech Bull 3×
        "WEBL",  # Direxion Daily Dow Jones Internet Bull 3×
        "FNGU",  # MicroSectors FANG+ Index 3× Leveraged
        "NAIL",  # Direxion Daily Homebuilders & Supplies Bull 3×
        "DPST",  # Direxion Daily Regional Banks Bull 3×
        "YINN",  # Direxion Daily FTSE China Bull 3×
        "DRN",  # Direxion Daily Real Estate Bull 3×
        "TMF",  # Direxion Daily 20+ Year Treasury Bull 3×
        "HIBL",  # Direxion Daily S&P 500 High Beta Bull 3×
        "MIDU",  # Direxion Daily Mid Cap Bull 3×
        "WANT",  # Direxion Daily Consumer Discretionary Bull 3×
        "CURE",  # Direxion Daily Healthcare Bull 3×
        "INDL",  # Direxion Daily MSCI India Bull 2×
        "GUSH",  # Direxion Daily S&P Oil & Gas E&P Bull 2×
        "NUGT",  # Direxion Daily Gold Miners Bull 2×
        "JNUG",  # Direxion Daily Junior Gold Miners Bull 2×
        "UCO",  # ProShares Ultra DJ-AIG Crude Oil 2×
        "SSO",  # ProShares Ultra S&P 500 2×
        "QLD",  # ProShares Ultra QQQ 2×
        "ROM",  # ProShares Ultra Technology 2×
        "UWM",  # ProShares Ultra Russell2000 2×
        # ── 3× Bear / Inverse ────────────────────────────────────────────────────
        "SQQQ",  # ProShares UltraPro Short QQQ
        "SPXS",  # Direxion Daily S&P 500 Bear 3×
        "SPXU",  # ProShares UltraPro Short S&P 500
        "SOXS",  # Direxion Daily Semiconductor Bear 3×
        "TECS",  # Direxion Daily Technology Bear 3×
        "FAZ",  # Direxion Daily Financial Bear 3×
        "TZA",  # Direxion Daily Small Cap Bear 3×
        "LABD",  # Direxion Daily S&P Biotech Bear 3×
        "FNGD",  # MicroSectors FANG+ Index −3× Inverse
        "YANG",  # Direxion Daily FTSE China Bear 3×
        "DRV",  # Direxion Daily Real Estate Bear 3×
        "TMV",  # Direxion Daily 20+ Year Treasury Bear 3×
        "HIBS",  # Direxion Daily S&P 500 High Beta Bear 3×
        "SRTY",  # ProShares UltraPro Short Russell2000
        "DRIP",  # Direxion Daily S&P Oil & Gas E&P Bear 2×
        "DUST",  # Direxion Daily Gold Miners Bear 2×
        "JDST",  # Direxion Daily Junior Gold Miners Bear 2×
        "SCO",  # ProShares UltraShort DJ-AIG Crude Oil 2×
        "SDS",  # ProShares UltraShort S&P 500 2×
        "QID",  # ProShares UltraShort QQQ 2×
        "REW",  # ProShares UltraShort Technology 2×
        "TWM",  # ProShares UltraShort Russell2000 2×
    }
)
mutants_x__make_plain_english__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__make_plain_english__mutmut)
def _make_plain_english(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_orig(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_1(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = None
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_2(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(None, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_3(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, None)
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_4(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get("move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_5(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, )
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_6(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"XXBUYXX": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_7(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"buy": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_8(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "XXriseXX", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_9(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "RISE", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_10(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "XXSELLXX": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_11(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "sell": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_12(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "XXfallXX", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_13(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "FALL", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_14(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "XXHOLDXX": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_15(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "hold": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_16(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "XXstay range-boundXX"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_17(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "STAY RANGE-BOUND"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_18(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "XXmoveXX")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_19(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "MOVE")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_20(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = None
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_21(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(None, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_22(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, None)
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_23(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_24(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, )
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_25(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("XXover the coming daysXX", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_26(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("OVER THE COMING DAYS", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_27(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "XXDaysXX"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_28(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_29(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "DAYS"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_30(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = None

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_31(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "XXhighXX" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_32(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "HIGH" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_33(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence > 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_34(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 76 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_35(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "XXmoderateXX" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_36(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "MODERATE" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_37(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence > 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_38(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 61 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_39(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "XXlowXX"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_40(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "LOW"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_41(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = None
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_42(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "XXposXX" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_43(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "POS" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_44(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action != "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_45(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "XXBUYXX" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_46(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "buy" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_47(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "XXnegXX"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_48(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "NEG"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_49(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = None
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_50(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["XXheadXX"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_51(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["HEAD"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_52(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent or r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_53(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get(None) == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_54(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("XXsentimentXX") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_55(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("SENTIMENT") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_56(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") != agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_57(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get(None)][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_58(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("XXheadXX")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_59(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("HEAD")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_60(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:4]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_61(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_62(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = None

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_63(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["XXheadXX"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_64(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["HEAD"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_65(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get(None)][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_66(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("XXheadXX")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_67(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("HEAD")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_68(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:3]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_69(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action != "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_70(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "XXHOLDXX":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_71(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "hold":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_72(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = None
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_73(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "XXBest to wait on the sidelines until a cleaner setup emerges.XX"
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_74(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_75(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "BEST TO WAIT ON THE SIDELINES UNTIL A CLEANER SETUP EMERGES."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_76(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = None
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_77(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = "XXXX"
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_78(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) > 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_79(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 3:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_80(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = None
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_81(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip(None)}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_82(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].lstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_83(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[1].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_84(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('XX.XX')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_85(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip(None)}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_86(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].lstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_87(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[2].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_88(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('XX.XX')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_89(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = None

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_90(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip(None)}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_91(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].lstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_92(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[1].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_93(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('XX.XX')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_94(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = None
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_95(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = "XXXX"
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_96(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry or target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_97(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = None
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_98(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry / 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_99(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) * entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_100(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(None) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_101(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target + entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_102(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 101
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_103(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = None

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_104(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'XXgainXX' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_105(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'GAIN' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_106(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action != 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_107(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'XXBUYXX' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_108(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'buy' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_109(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'XXdropXX'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_110(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'DROP'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_111(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = None

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_112(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "XXsummaryXX": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_113(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "SUMMARY": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_114(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "XXtimeframeXX": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_115(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "TIMEFRAME": tf_long,
        "tf_short": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_116(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "XXtf_shortXX": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_117(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "TF_SHORT": tf_short,
        "top_reasons": top,
    }


def x__make_plain_english__mutmut_118(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "XXtop_reasonsXX": top,
    }


def x__make_plain_english__mutmut_119(
    action: str, ticker: str, style: str, rationale: list, confidence: float, entry, stop, target
) -> dict:
    direction = {"BUY": "rise", "SELL": "fall", "HOLD": "stay range-bound"}.get(action, "move")
    tf_long, tf_short = _TIMEFRAME.get(style, ("over the coming days", "Days"))
    conf_word = "high" if confidence >= 75 else "moderate" if confidence >= 60 else "low"

    agree_sent = "pos" if action == "BUY" else "neg"
    top = [r["head"] for r in rationale if r.get("sentiment") == agree_sent and r.get("head")][:3]
    if not top:
        top = [r["head"] for r in rationale if r.get("head")][:2]

    if action == "HOLD":
        summary = (
            f"{ticker} is sending mixed signals — no clear edge in either direction right now. "
            f"Indicators are roughly balanced ({confidence:.0f}% confidence this is a no-trade setup). "
            "Best to wait on the sidelines until a cleaner setup emerges."
        )
    else:
        why = ""
        if len(top) >= 2:
            why = f" Driven by: {top[0].rstrip('.')}; and {top[1].rstrip('.')}."
        elif top:
            why = f" Main signal: {top[0].rstrip('.')}."

        move_text = ""
        if entry and target:
            pct = abs(target - entry) / entry * 100
            move_text = f" If the move plays out, the target implies a {pct:.1f}% {'gain' if action == 'BUY' else 'drop'} from entry."

        summary = (
            f"The system expects {ticker} to {direction} {tf_long}, "
            f"with {conf_word} confidence ({confidence:.0f}%).{why}{move_text}"
        )

    return {
        "summary": summary,
        "timeframe": tf_long,
        "tf_short": tf_short,
        "TOP_REASONS": top,
    }

mutants_x__make_plain_english__mutmut['_mutmut_orig'] = x__make_plain_english__mutmut_orig # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_1'] = x__make_plain_english__mutmut_1 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_2'] = x__make_plain_english__mutmut_2 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_3'] = x__make_plain_english__mutmut_3 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_4'] = x__make_plain_english__mutmut_4 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_5'] = x__make_plain_english__mutmut_5 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_6'] = x__make_plain_english__mutmut_6 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_7'] = x__make_plain_english__mutmut_7 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_8'] = x__make_plain_english__mutmut_8 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_9'] = x__make_plain_english__mutmut_9 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_10'] = x__make_plain_english__mutmut_10 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_11'] = x__make_plain_english__mutmut_11 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_12'] = x__make_plain_english__mutmut_12 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_13'] = x__make_plain_english__mutmut_13 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_14'] = x__make_plain_english__mutmut_14 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_15'] = x__make_plain_english__mutmut_15 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_16'] = x__make_plain_english__mutmut_16 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_17'] = x__make_plain_english__mutmut_17 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_18'] = x__make_plain_english__mutmut_18 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_19'] = x__make_plain_english__mutmut_19 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_20'] = x__make_plain_english__mutmut_20 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_21'] = x__make_plain_english__mutmut_21 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_22'] = x__make_plain_english__mutmut_22 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_23'] = x__make_plain_english__mutmut_23 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_24'] = x__make_plain_english__mutmut_24 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_25'] = x__make_plain_english__mutmut_25 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_26'] = x__make_plain_english__mutmut_26 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_27'] = x__make_plain_english__mutmut_27 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_28'] = x__make_plain_english__mutmut_28 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_29'] = x__make_plain_english__mutmut_29 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_30'] = x__make_plain_english__mutmut_30 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_31'] = x__make_plain_english__mutmut_31 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_32'] = x__make_plain_english__mutmut_32 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_33'] = x__make_plain_english__mutmut_33 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_34'] = x__make_plain_english__mutmut_34 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_35'] = x__make_plain_english__mutmut_35 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_36'] = x__make_plain_english__mutmut_36 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_37'] = x__make_plain_english__mutmut_37 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_38'] = x__make_plain_english__mutmut_38 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_39'] = x__make_plain_english__mutmut_39 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_40'] = x__make_plain_english__mutmut_40 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_41'] = x__make_plain_english__mutmut_41 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_42'] = x__make_plain_english__mutmut_42 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_43'] = x__make_plain_english__mutmut_43 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_44'] = x__make_plain_english__mutmut_44 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_45'] = x__make_plain_english__mutmut_45 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_46'] = x__make_plain_english__mutmut_46 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_47'] = x__make_plain_english__mutmut_47 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_48'] = x__make_plain_english__mutmut_48 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_49'] = x__make_plain_english__mutmut_49 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_50'] = x__make_plain_english__mutmut_50 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_51'] = x__make_plain_english__mutmut_51 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_52'] = x__make_plain_english__mutmut_52 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_53'] = x__make_plain_english__mutmut_53 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_54'] = x__make_plain_english__mutmut_54 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_55'] = x__make_plain_english__mutmut_55 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_56'] = x__make_plain_english__mutmut_56 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_57'] = x__make_plain_english__mutmut_57 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_58'] = x__make_plain_english__mutmut_58 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_59'] = x__make_plain_english__mutmut_59 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_60'] = x__make_plain_english__mutmut_60 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_61'] = x__make_plain_english__mutmut_61 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_62'] = x__make_plain_english__mutmut_62 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_63'] = x__make_plain_english__mutmut_63 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_64'] = x__make_plain_english__mutmut_64 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_65'] = x__make_plain_english__mutmut_65 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_66'] = x__make_plain_english__mutmut_66 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_67'] = x__make_plain_english__mutmut_67 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_68'] = x__make_plain_english__mutmut_68 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_69'] = x__make_plain_english__mutmut_69 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_70'] = x__make_plain_english__mutmut_70 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_71'] = x__make_plain_english__mutmut_71 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_72'] = x__make_plain_english__mutmut_72 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_73'] = x__make_plain_english__mutmut_73 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_74'] = x__make_plain_english__mutmut_74 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_75'] = x__make_plain_english__mutmut_75 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_76'] = x__make_plain_english__mutmut_76 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_77'] = x__make_plain_english__mutmut_77 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_78'] = x__make_plain_english__mutmut_78 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_79'] = x__make_plain_english__mutmut_79 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_80'] = x__make_plain_english__mutmut_80 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_81'] = x__make_plain_english__mutmut_81 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_82'] = x__make_plain_english__mutmut_82 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_83'] = x__make_plain_english__mutmut_83 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_84'] = x__make_plain_english__mutmut_84 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_85'] = x__make_plain_english__mutmut_85 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_86'] = x__make_plain_english__mutmut_86 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_87'] = x__make_plain_english__mutmut_87 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_88'] = x__make_plain_english__mutmut_88 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_89'] = x__make_plain_english__mutmut_89 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_90'] = x__make_plain_english__mutmut_90 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_91'] = x__make_plain_english__mutmut_91 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_92'] = x__make_plain_english__mutmut_92 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_93'] = x__make_plain_english__mutmut_93 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_94'] = x__make_plain_english__mutmut_94 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_95'] = x__make_plain_english__mutmut_95 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_96'] = x__make_plain_english__mutmut_96 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_97'] = x__make_plain_english__mutmut_97 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_98'] = x__make_plain_english__mutmut_98 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_99'] = x__make_plain_english__mutmut_99 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_100'] = x__make_plain_english__mutmut_100 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_101'] = x__make_plain_english__mutmut_101 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_102'] = x__make_plain_english__mutmut_102 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_103'] = x__make_plain_english__mutmut_103 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_104'] = x__make_plain_english__mutmut_104 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_105'] = x__make_plain_english__mutmut_105 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_106'] = x__make_plain_english__mutmut_106 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_107'] = x__make_plain_english__mutmut_107 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_108'] = x__make_plain_english__mutmut_108 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_109'] = x__make_plain_english__mutmut_109 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_110'] = x__make_plain_english__mutmut_110 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_111'] = x__make_plain_english__mutmut_111 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_112'] = x__make_plain_english__mutmut_112 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_113'] = x__make_plain_english__mutmut_113 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_114'] = x__make_plain_english__mutmut_114 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_115'] = x__make_plain_english__mutmut_115 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_116'] = x__make_plain_english__mutmut_116 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_117'] = x__make_plain_english__mutmut_117 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_118'] = x__make_plain_english__mutmut_118 # type: ignore # mutmut generated
mutants_x__make_plain_english__mutmut['x__make_plain_english__mutmut_119'] = x__make_plain_english__mutmut_119 # type: ignore # mutmut generated
