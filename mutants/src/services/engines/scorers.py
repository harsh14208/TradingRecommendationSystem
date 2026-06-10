"""
services/engines/scorers.py

Decomposed scoring blocks utilizing the ScoringContext object.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from services.engines.context import ScoringContext

log = logging.getLogger("signal.trade.scorers")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_score_moving_averages_block__mutmut: MutantDict = {}  # type: ignore

@_mutmut_mutated(mutants_x_score_moving_averages_block__mutmut)
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

def x_score_moving_averages_block__mutmut_orig(ctx: ScoringContext) -> None:
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

def x_score_moving_averages_block__mutmut_1(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = None
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_2(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = None
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_3(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get(None)
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_4(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("XXsma50XX")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_5(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("SMA50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_6(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = None
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_7(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get(None)
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_8(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("XXsma200XX")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_9(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("SMA200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_10(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = None
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_11(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") and {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_12(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get(None) or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_13(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("XXpoly_indicatorsXX") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_14(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("POLY_INDICATORS") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_15(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = None
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_16(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(None, sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_17(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, None, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_18(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, None, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_19(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, None)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_20(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(sma50, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_21(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma200, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_22(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, poly_ind)
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_23(ctx: ScoringContext) -> None:
    """
    Score SMA200, SMA50, Golden/Death Cross, and EMA200 double-confirmation.
    Caps the family at ±30.
    """
    from services.signal_scoring import score_moving_averages
    
    price = ctx.price
    sma50 = ctx.tech.get("sma50")
    sma200 = ctx.tech.get("sma200")
    poly_ind = ctx.tech.get("poly_indicators") or {}
    
    ma_delta, ma_rat = score_moving_averages(price, sma50, sma200, )
    ctx.ma_score += ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_24(ctx: ScoringContext) -> None:
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
    ctx.ma_score = ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_25(ctx: ScoringContext) -> None:
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
    ctx.ma_score -= ma_delta
    ctx.rationale.extend(ma_rat)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_26(ctx: ScoringContext) -> None:
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
    ctx.rationale.extend(None)
    
    if not ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_27(ctx: ScoringContext) -> None:
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
    
    if ctx._is_low_atr:
        ctx.score += max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_28(ctx: ScoringContext) -> None:
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
        ctx.score = max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_29(ctx: ScoringContext) -> None:
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
        ctx.score -= max(-30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_30(ctx: ScoringContext) -> None:
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
        ctx.score += max(None, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_31(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, None)

def x_score_moving_averages_block__mutmut_32(ctx: ScoringContext) -> None:
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
        ctx.score += max(min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_33(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, )

def x_score_moving_averages_block__mutmut_34(ctx: ScoringContext) -> None:
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
        ctx.score += max(+30.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_35(ctx: ScoringContext) -> None:
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
        ctx.score += max(-31.0, min(30.0, ctx.ma_score))

def x_score_moving_averages_block__mutmut_36(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, min(None, ctx.ma_score))

def x_score_moving_averages_block__mutmut_37(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, min(30.0, None))

def x_score_moving_averages_block__mutmut_38(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, min(ctx.ma_score))

def x_score_moving_averages_block__mutmut_39(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, min(30.0, ))

def x_score_moving_averages_block__mutmut_40(ctx: ScoringContext) -> None:
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
        ctx.score += max(-30.0, min(31.0, ctx.ma_score))

mutants_x_score_moving_averages_block__mutmut['_mutmut_orig'] = x_score_moving_averages_block__mutmut_orig # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_1'] = x_score_moving_averages_block__mutmut_1 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_2'] = x_score_moving_averages_block__mutmut_2 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_3'] = x_score_moving_averages_block__mutmut_3 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_4'] = x_score_moving_averages_block__mutmut_4 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_5'] = x_score_moving_averages_block__mutmut_5 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_6'] = x_score_moving_averages_block__mutmut_6 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_7'] = x_score_moving_averages_block__mutmut_7 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_8'] = x_score_moving_averages_block__mutmut_8 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_9'] = x_score_moving_averages_block__mutmut_9 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_10'] = x_score_moving_averages_block__mutmut_10 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_11'] = x_score_moving_averages_block__mutmut_11 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_12'] = x_score_moving_averages_block__mutmut_12 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_13'] = x_score_moving_averages_block__mutmut_13 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_14'] = x_score_moving_averages_block__mutmut_14 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_15'] = x_score_moving_averages_block__mutmut_15 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_16'] = x_score_moving_averages_block__mutmut_16 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_17'] = x_score_moving_averages_block__mutmut_17 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_18'] = x_score_moving_averages_block__mutmut_18 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_19'] = x_score_moving_averages_block__mutmut_19 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_20'] = x_score_moving_averages_block__mutmut_20 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_21'] = x_score_moving_averages_block__mutmut_21 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_22'] = x_score_moving_averages_block__mutmut_22 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_23'] = x_score_moving_averages_block__mutmut_23 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_24'] = x_score_moving_averages_block__mutmut_24 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_25'] = x_score_moving_averages_block__mutmut_25 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_26'] = x_score_moving_averages_block__mutmut_26 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_27'] = x_score_moving_averages_block__mutmut_27 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_28'] = x_score_moving_averages_block__mutmut_28 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_29'] = x_score_moving_averages_block__mutmut_29 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_30'] = x_score_moving_averages_block__mutmut_30 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_31'] = x_score_moving_averages_block__mutmut_31 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_32'] = x_score_moving_averages_block__mutmut_32 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_33'] = x_score_moving_averages_block__mutmut_33 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_34'] = x_score_moving_averages_block__mutmut_34 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_35'] = x_score_moving_averages_block__mutmut_35 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_36'] = x_score_moving_averages_block__mutmut_36 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_37'] = x_score_moving_averages_block__mutmut_37 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_38'] = x_score_moving_averages_block__mutmut_38 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_39'] = x_score_moving_averages_block__mutmut_39 # type: ignore # mutmut generated
mutants_x_score_moving_averages_block__mutmut['x_score_moving_averages_block__mutmut_40'] = x_score_moving_averages_block__mutmut_40 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_score_bollinger_bands_block__mutmut)
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_orig(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_1(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = None
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_2(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get(None)
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_3(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("XXbb_upperXX")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_4(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("BB_UPPER")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_5(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = None
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_6(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get(None)
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_7(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("XXbb_lowerXX")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_8(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("BB_LOWER")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_9(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = None
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_10(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get(None)
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_11(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("XXbb_pct_bXX")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_12(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("BB_PCT_B")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_13(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = None
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_14(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get(None)
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_15(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("XXrsiXX")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_16(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("RSI")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_17(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = None
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_18(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = None
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_19(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 51.0
    if bb_pct_b is not None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_20(ctx: ScoringContext) -> None:
    """
    Score tiered BB%B + RSI confluence or absolute band touches.
    """
    bb_upper = ctx.tech.get("bb_upper")
    bb_lower = ctx.tech.get("bb_lower")
    bb_pct_b = ctx.tech.get("bb_pct_b")
    rsi = ctx.tech.get("rsi")
    price = ctx.price
    
    bb_rsi = rsi if isinstance(rsi, (int, float)) else 50.0
    if bb_pct_b is None:
        if bb_pct_b < 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_21(ctx: ScoringContext) -> None:
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
        if bb_pct_b <= 0.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_22(ctx: ScoringContext) -> None:
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
        if bb_pct_b < 1.05:
            if bb_rsi < 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_23(ctx: ScoringContext) -> None:
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
            if bb_rsi <= 35:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_24(ctx: ScoringContext) -> None:
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
            if bb_rsi < 36:
                bb_pts = 18.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_25(ctx: ScoringContext) -> None:
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
                bb_pts = None
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_26(ctx: ScoringContext) -> None:
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
                bb_pts = 19.0
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_27(ctx: ScoringContext) -> None:
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
                bb_body = None
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_28(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi <= 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_29(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 46:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_30(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = None
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_31(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 13.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_32(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = None
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_33(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = None
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_34(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 7.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_35(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = None
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_36(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score = bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_37(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score -= bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_38(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append(None)
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_39(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "XXsrcXX": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_40(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "SRC": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_41(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "XXTechnicalXX",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_42(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_43(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "TECHNICAL",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_44(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "XXheadXX": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_45(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "HEAD": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_46(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "XXBB Extreme OversoldXX",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_47(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "bb extreme oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_48(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB EXTREME OVERSOLD",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_49(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "XXbodyXX": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_50(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "BODY": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_51(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "XXsentimentXX": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_52(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "SENTIMENT": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_53(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "XXposXX",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_54(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "POS",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_55(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "XXmetaXX": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_56(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "META": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_57(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b <= 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_58(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 1.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_59(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi <= 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_60(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 36:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_61(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score = 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_62(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score -= 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_63(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 11.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_64(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append(None)
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_65(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "XXsrcXX": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_66(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "SRC": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_67(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "XXTechnicalXX",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_68(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_69(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "TECHNICAL",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_70(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "XXheadXX": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_71(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "HEAD": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_72(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "XXBB Oversold + RSI ConfirmedXX",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_73(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "bb oversold + rsi confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_74(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB OVERSOLD + RSI CONFIRMED",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_75(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "XXbodyXX": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_76(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "BODY": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_77(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "XXsentimentXX": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_78(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "SENTIMENT": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_79(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "XXposXX",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_80(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "POS",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_81(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "XXmetaXX": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_82(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "META": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_83(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi <= 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_84(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 46:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_85(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score = 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_86(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score -= 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_87(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 6.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_88(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append(None)
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_89(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "XXsrcXX": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_90(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "SRC": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_91(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "XXTechnicalXX",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_92(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_93(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "TECHNICAL",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_94(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "XXheadXX": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_95(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "HEAD": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_96(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "XXBB Near Lower BandXX",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_97(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "bb near lower band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_98(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB NEAR LOWER BAND",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_99(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "XXbodyXX": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_100(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "BODY": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_101(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "XXsentimentXX": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_102(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "SENTIMENT": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_103(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "XXposXX",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_104(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "POS",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_105(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "XXmetaXX": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_106(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "META": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_107(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b >= 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_108(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 1.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_109(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi >= 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_110(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 66:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_111(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score = 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_112(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score += 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_113(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 15.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_114(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append(None)
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_115(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "XXsrcXX": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_116(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "SRC": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_117(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "XXTechnicalXX",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_118(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_119(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "TECHNICAL",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_120(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "XXheadXX": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_121(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "HEAD": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_122(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "XXBB Extreme OverboughtXX",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_123(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "bb extreme overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_124(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB EXTREME OVERBOUGHT",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_125(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "XXbodyXX": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_126(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "BODY": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_127(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "XXsentimentXX": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_128(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "SENTIMENT": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_129(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "XXnegXX",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_130(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "NEG",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_131(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "XXmetaXX": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_132(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "META": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_133(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi >= 55:
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_134(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 56:
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_135(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score = 8.0
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_136(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score += 8.0
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_137(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 9.0
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_138(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score = 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_139(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score += 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_140(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 5.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_141(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b >= 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_142(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 1.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_143(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi >= 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_144(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 66:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_145(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score = 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_146(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score += 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_147(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 9.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_148(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi >= 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_149(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 56:
                ctx.mean_rev_score -= 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_150(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score = 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_151(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score += 4.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_152(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 5.0
    elif bb_lower and bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_153(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 8.0
            elif bb_upper:
                ctx.mean_rev_score -= 4.0
        elif bb_pct_b > 0.85:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 8.0
            elif bb_rsi > 55:
                ctx.mean_rev_score -= 4.0
    elif bb_lower or bb_upper:
        if price <= bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_154(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
        if price < bb_lower * 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_155(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
        if price <= bb_lower / 1.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_156(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
        if price <= bb_lower * 2.005:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_157(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.mean_rev_score = 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_158(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_159(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.mean_rev_score += 7.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_160(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append(None)
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_161(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "XXsrcXX": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_162(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "SRC": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_163(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "XXTechnicalXX",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_164(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_165(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "TECHNICAL",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_166(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "XXheadXX": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_167(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "HEAD": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_168(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "XXLower Bollinger Band TouchXX",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_169(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "lower bollinger band touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_170(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "LOWER BOLLINGER BAND TOUCH",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_171(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "XXbodyXX": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_172(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "BODY": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_173(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "XXPrice at lower BB — potential mean-reversion bounce.XX",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_174(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "price at lower bb — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_175(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "PRICE AT LOWER BB — POTENTIAL MEAN-REVERSION BOUNCE.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_176(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "XXsentimentXX": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_177(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "SENTIMENT": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_178(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "XXposXX",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_179(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "POS",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_180(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "XXmetaXX": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_181(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "META": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_182(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price > bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_183(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper / 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_184(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 1.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_185(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score = 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_186(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score += 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_187(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 7.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_188(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append(None)


def x_score_bollinger_bands_block__mutmut_189(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "XXsrcXX": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_190(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "SRC": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_191(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "XXTechnicalXX",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_192(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_193(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "TECHNICAL",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_194(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "XXheadXX": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_195(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "HEAD": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_196(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "XXUpper Bollinger Band TouchXX",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_197(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "upper bollinger band touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_198(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "UPPER BOLLINGER BAND TOUCH",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_199(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "XXbodyXX": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_200(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "BODY": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_201(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "XXPrice at upper BB — potential overextension.XX",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_202(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "price at upper bb — potential overextension.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_203(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "PRICE AT UPPER BB — POTENTIAL OVEREXTENSION.",
                "sentiment": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_204(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "XXsentimentXX": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_205(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "SENTIMENT": "neg",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_206(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "XXnegXX",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_207(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "NEG",
                "meta": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_208(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "XXmetaXX": f"BB Upper ${bb_upper:.2f}",
            })


def x_score_bollinger_bands_block__mutmut_209(ctx: ScoringContext) -> None:
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
                bb_body = f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — deep oversold confluence. Highest-probability MR setup."
            elif bb_rsi < 45:
                bb_pts = 12.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme, RSI={bb_rsi:.0f} confirming oversold."
            else:
                bb_pts = 6.0
                bb_body = f"BB%B={bb_pct_b:.2f} at lower extreme — price statistically stretched."
            ctx.mean_rev_score += bb_pts
            ctx.rationale.append({
                "src": "Technical",
                "head": "BB Extreme Oversold",
                "body": bb_body,
                "sentiment": "pos",
                "meta": f"BB%B={bb_pct_b:.2f} | RSI={bb_rsi:.0f}",
            })
        elif bb_pct_b < 0.15:
            if bb_rsi < 35:
                ctx.mean_rev_score += 10.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Oversold + RSI Confirmed",
                    "body": f"BB%B={bb_pct_b:.2f}, RSI={bb_rsi:.0f} — both in oversold territory.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
            elif bb_rsi < 45:
                ctx.mean_rev_score += 5.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Near Lower Band",
                    "body": f"BB%B={bb_pct_b:.2f} — approaching oversold, RSI={bb_rsi:.0f} softening.",
                    "sentiment": "pos",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
        elif bb_pct_b > 0.95:
            if bb_rsi > 65:
                ctx.mean_rev_score -= 14.0
                ctx.rationale.append({
                    "src": "Technical",
                    "head": "BB Extreme Overbought",
                    "body": f"BB%B={bb_pct_b:.2f} + RSI={bb_rsi:.0f} — both overbought. High distribution risk.",
                    "sentiment": "neg",
                    "meta": f"BB%B={bb_pct_b:.2f}",
                })
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
            ctx.rationale.append({
                "src": "Technical",
                "head": "Lower Bollinger Band Touch",
                "body": "Price at lower BB — potential mean-reversion bounce.",
                "sentiment": "pos",
                "meta": f"BB Lower ${bb_lower:.2f}",
            })
        elif price >= bb_upper * 0.995:
            ctx.mean_rev_score -= 6.0
            ctx.rationale.append({
                "src": "Technical",
                "head": "Upper Bollinger Band Touch",
                "body": "Price at upper BB — potential overextension.",
                "sentiment": "neg",
                "META": f"BB Upper ${bb_upper:.2f}",
            })

mutants_x_score_bollinger_bands_block__mutmut['_mutmut_orig'] = x_score_bollinger_bands_block__mutmut_orig # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_1'] = x_score_bollinger_bands_block__mutmut_1 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_2'] = x_score_bollinger_bands_block__mutmut_2 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_3'] = x_score_bollinger_bands_block__mutmut_3 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_4'] = x_score_bollinger_bands_block__mutmut_4 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_5'] = x_score_bollinger_bands_block__mutmut_5 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_6'] = x_score_bollinger_bands_block__mutmut_6 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_7'] = x_score_bollinger_bands_block__mutmut_7 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_8'] = x_score_bollinger_bands_block__mutmut_8 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_9'] = x_score_bollinger_bands_block__mutmut_9 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_10'] = x_score_bollinger_bands_block__mutmut_10 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_11'] = x_score_bollinger_bands_block__mutmut_11 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_12'] = x_score_bollinger_bands_block__mutmut_12 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_13'] = x_score_bollinger_bands_block__mutmut_13 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_14'] = x_score_bollinger_bands_block__mutmut_14 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_15'] = x_score_bollinger_bands_block__mutmut_15 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_16'] = x_score_bollinger_bands_block__mutmut_16 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_17'] = x_score_bollinger_bands_block__mutmut_17 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_18'] = x_score_bollinger_bands_block__mutmut_18 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_19'] = x_score_bollinger_bands_block__mutmut_19 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_20'] = x_score_bollinger_bands_block__mutmut_20 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_21'] = x_score_bollinger_bands_block__mutmut_21 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_22'] = x_score_bollinger_bands_block__mutmut_22 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_23'] = x_score_bollinger_bands_block__mutmut_23 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_24'] = x_score_bollinger_bands_block__mutmut_24 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_25'] = x_score_bollinger_bands_block__mutmut_25 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_26'] = x_score_bollinger_bands_block__mutmut_26 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_27'] = x_score_bollinger_bands_block__mutmut_27 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_28'] = x_score_bollinger_bands_block__mutmut_28 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_29'] = x_score_bollinger_bands_block__mutmut_29 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_30'] = x_score_bollinger_bands_block__mutmut_30 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_31'] = x_score_bollinger_bands_block__mutmut_31 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_32'] = x_score_bollinger_bands_block__mutmut_32 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_33'] = x_score_bollinger_bands_block__mutmut_33 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_34'] = x_score_bollinger_bands_block__mutmut_34 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_35'] = x_score_bollinger_bands_block__mutmut_35 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_36'] = x_score_bollinger_bands_block__mutmut_36 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_37'] = x_score_bollinger_bands_block__mutmut_37 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_38'] = x_score_bollinger_bands_block__mutmut_38 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_39'] = x_score_bollinger_bands_block__mutmut_39 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_40'] = x_score_bollinger_bands_block__mutmut_40 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_41'] = x_score_bollinger_bands_block__mutmut_41 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_42'] = x_score_bollinger_bands_block__mutmut_42 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_43'] = x_score_bollinger_bands_block__mutmut_43 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_44'] = x_score_bollinger_bands_block__mutmut_44 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_45'] = x_score_bollinger_bands_block__mutmut_45 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_46'] = x_score_bollinger_bands_block__mutmut_46 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_47'] = x_score_bollinger_bands_block__mutmut_47 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_48'] = x_score_bollinger_bands_block__mutmut_48 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_49'] = x_score_bollinger_bands_block__mutmut_49 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_50'] = x_score_bollinger_bands_block__mutmut_50 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_51'] = x_score_bollinger_bands_block__mutmut_51 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_52'] = x_score_bollinger_bands_block__mutmut_52 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_53'] = x_score_bollinger_bands_block__mutmut_53 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_54'] = x_score_bollinger_bands_block__mutmut_54 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_55'] = x_score_bollinger_bands_block__mutmut_55 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_56'] = x_score_bollinger_bands_block__mutmut_56 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_57'] = x_score_bollinger_bands_block__mutmut_57 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_58'] = x_score_bollinger_bands_block__mutmut_58 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_59'] = x_score_bollinger_bands_block__mutmut_59 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_60'] = x_score_bollinger_bands_block__mutmut_60 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_61'] = x_score_bollinger_bands_block__mutmut_61 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_62'] = x_score_bollinger_bands_block__mutmut_62 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_63'] = x_score_bollinger_bands_block__mutmut_63 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_64'] = x_score_bollinger_bands_block__mutmut_64 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_65'] = x_score_bollinger_bands_block__mutmut_65 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_66'] = x_score_bollinger_bands_block__mutmut_66 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_67'] = x_score_bollinger_bands_block__mutmut_67 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_68'] = x_score_bollinger_bands_block__mutmut_68 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_69'] = x_score_bollinger_bands_block__mutmut_69 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_70'] = x_score_bollinger_bands_block__mutmut_70 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_71'] = x_score_bollinger_bands_block__mutmut_71 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_72'] = x_score_bollinger_bands_block__mutmut_72 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_73'] = x_score_bollinger_bands_block__mutmut_73 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_74'] = x_score_bollinger_bands_block__mutmut_74 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_75'] = x_score_bollinger_bands_block__mutmut_75 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_76'] = x_score_bollinger_bands_block__mutmut_76 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_77'] = x_score_bollinger_bands_block__mutmut_77 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_78'] = x_score_bollinger_bands_block__mutmut_78 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_79'] = x_score_bollinger_bands_block__mutmut_79 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_80'] = x_score_bollinger_bands_block__mutmut_80 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_81'] = x_score_bollinger_bands_block__mutmut_81 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_82'] = x_score_bollinger_bands_block__mutmut_82 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_83'] = x_score_bollinger_bands_block__mutmut_83 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_84'] = x_score_bollinger_bands_block__mutmut_84 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_85'] = x_score_bollinger_bands_block__mutmut_85 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_86'] = x_score_bollinger_bands_block__mutmut_86 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_87'] = x_score_bollinger_bands_block__mutmut_87 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_88'] = x_score_bollinger_bands_block__mutmut_88 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_89'] = x_score_bollinger_bands_block__mutmut_89 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_90'] = x_score_bollinger_bands_block__mutmut_90 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_91'] = x_score_bollinger_bands_block__mutmut_91 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_92'] = x_score_bollinger_bands_block__mutmut_92 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_93'] = x_score_bollinger_bands_block__mutmut_93 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_94'] = x_score_bollinger_bands_block__mutmut_94 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_95'] = x_score_bollinger_bands_block__mutmut_95 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_96'] = x_score_bollinger_bands_block__mutmut_96 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_97'] = x_score_bollinger_bands_block__mutmut_97 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_98'] = x_score_bollinger_bands_block__mutmut_98 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_99'] = x_score_bollinger_bands_block__mutmut_99 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_100'] = x_score_bollinger_bands_block__mutmut_100 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_101'] = x_score_bollinger_bands_block__mutmut_101 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_102'] = x_score_bollinger_bands_block__mutmut_102 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_103'] = x_score_bollinger_bands_block__mutmut_103 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_104'] = x_score_bollinger_bands_block__mutmut_104 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_105'] = x_score_bollinger_bands_block__mutmut_105 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_106'] = x_score_bollinger_bands_block__mutmut_106 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_107'] = x_score_bollinger_bands_block__mutmut_107 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_108'] = x_score_bollinger_bands_block__mutmut_108 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_109'] = x_score_bollinger_bands_block__mutmut_109 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_110'] = x_score_bollinger_bands_block__mutmut_110 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_111'] = x_score_bollinger_bands_block__mutmut_111 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_112'] = x_score_bollinger_bands_block__mutmut_112 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_113'] = x_score_bollinger_bands_block__mutmut_113 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_114'] = x_score_bollinger_bands_block__mutmut_114 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_115'] = x_score_bollinger_bands_block__mutmut_115 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_116'] = x_score_bollinger_bands_block__mutmut_116 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_117'] = x_score_bollinger_bands_block__mutmut_117 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_118'] = x_score_bollinger_bands_block__mutmut_118 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_119'] = x_score_bollinger_bands_block__mutmut_119 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_120'] = x_score_bollinger_bands_block__mutmut_120 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_121'] = x_score_bollinger_bands_block__mutmut_121 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_122'] = x_score_bollinger_bands_block__mutmut_122 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_123'] = x_score_bollinger_bands_block__mutmut_123 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_124'] = x_score_bollinger_bands_block__mutmut_124 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_125'] = x_score_bollinger_bands_block__mutmut_125 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_126'] = x_score_bollinger_bands_block__mutmut_126 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_127'] = x_score_bollinger_bands_block__mutmut_127 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_128'] = x_score_bollinger_bands_block__mutmut_128 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_129'] = x_score_bollinger_bands_block__mutmut_129 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_130'] = x_score_bollinger_bands_block__mutmut_130 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_131'] = x_score_bollinger_bands_block__mutmut_131 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_132'] = x_score_bollinger_bands_block__mutmut_132 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_133'] = x_score_bollinger_bands_block__mutmut_133 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_134'] = x_score_bollinger_bands_block__mutmut_134 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_135'] = x_score_bollinger_bands_block__mutmut_135 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_136'] = x_score_bollinger_bands_block__mutmut_136 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_137'] = x_score_bollinger_bands_block__mutmut_137 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_138'] = x_score_bollinger_bands_block__mutmut_138 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_139'] = x_score_bollinger_bands_block__mutmut_139 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_140'] = x_score_bollinger_bands_block__mutmut_140 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_141'] = x_score_bollinger_bands_block__mutmut_141 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_142'] = x_score_bollinger_bands_block__mutmut_142 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_143'] = x_score_bollinger_bands_block__mutmut_143 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_144'] = x_score_bollinger_bands_block__mutmut_144 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_145'] = x_score_bollinger_bands_block__mutmut_145 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_146'] = x_score_bollinger_bands_block__mutmut_146 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_147'] = x_score_bollinger_bands_block__mutmut_147 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_148'] = x_score_bollinger_bands_block__mutmut_148 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_149'] = x_score_bollinger_bands_block__mutmut_149 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_150'] = x_score_bollinger_bands_block__mutmut_150 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_151'] = x_score_bollinger_bands_block__mutmut_151 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_152'] = x_score_bollinger_bands_block__mutmut_152 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_153'] = x_score_bollinger_bands_block__mutmut_153 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_154'] = x_score_bollinger_bands_block__mutmut_154 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_155'] = x_score_bollinger_bands_block__mutmut_155 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_156'] = x_score_bollinger_bands_block__mutmut_156 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_157'] = x_score_bollinger_bands_block__mutmut_157 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_158'] = x_score_bollinger_bands_block__mutmut_158 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_159'] = x_score_bollinger_bands_block__mutmut_159 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_160'] = x_score_bollinger_bands_block__mutmut_160 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_161'] = x_score_bollinger_bands_block__mutmut_161 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_162'] = x_score_bollinger_bands_block__mutmut_162 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_163'] = x_score_bollinger_bands_block__mutmut_163 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_164'] = x_score_bollinger_bands_block__mutmut_164 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_165'] = x_score_bollinger_bands_block__mutmut_165 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_166'] = x_score_bollinger_bands_block__mutmut_166 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_167'] = x_score_bollinger_bands_block__mutmut_167 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_168'] = x_score_bollinger_bands_block__mutmut_168 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_169'] = x_score_bollinger_bands_block__mutmut_169 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_170'] = x_score_bollinger_bands_block__mutmut_170 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_171'] = x_score_bollinger_bands_block__mutmut_171 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_172'] = x_score_bollinger_bands_block__mutmut_172 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_173'] = x_score_bollinger_bands_block__mutmut_173 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_174'] = x_score_bollinger_bands_block__mutmut_174 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_175'] = x_score_bollinger_bands_block__mutmut_175 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_176'] = x_score_bollinger_bands_block__mutmut_176 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_177'] = x_score_bollinger_bands_block__mutmut_177 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_178'] = x_score_bollinger_bands_block__mutmut_178 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_179'] = x_score_bollinger_bands_block__mutmut_179 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_180'] = x_score_bollinger_bands_block__mutmut_180 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_181'] = x_score_bollinger_bands_block__mutmut_181 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_182'] = x_score_bollinger_bands_block__mutmut_182 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_183'] = x_score_bollinger_bands_block__mutmut_183 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_184'] = x_score_bollinger_bands_block__mutmut_184 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_185'] = x_score_bollinger_bands_block__mutmut_185 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_186'] = x_score_bollinger_bands_block__mutmut_186 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_187'] = x_score_bollinger_bands_block__mutmut_187 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_188'] = x_score_bollinger_bands_block__mutmut_188 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_189'] = x_score_bollinger_bands_block__mutmut_189 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_190'] = x_score_bollinger_bands_block__mutmut_190 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_191'] = x_score_bollinger_bands_block__mutmut_191 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_192'] = x_score_bollinger_bands_block__mutmut_192 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_193'] = x_score_bollinger_bands_block__mutmut_193 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_194'] = x_score_bollinger_bands_block__mutmut_194 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_195'] = x_score_bollinger_bands_block__mutmut_195 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_196'] = x_score_bollinger_bands_block__mutmut_196 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_197'] = x_score_bollinger_bands_block__mutmut_197 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_198'] = x_score_bollinger_bands_block__mutmut_198 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_199'] = x_score_bollinger_bands_block__mutmut_199 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_200'] = x_score_bollinger_bands_block__mutmut_200 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_201'] = x_score_bollinger_bands_block__mutmut_201 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_202'] = x_score_bollinger_bands_block__mutmut_202 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_203'] = x_score_bollinger_bands_block__mutmut_203 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_204'] = x_score_bollinger_bands_block__mutmut_204 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_205'] = x_score_bollinger_bands_block__mutmut_205 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_206'] = x_score_bollinger_bands_block__mutmut_206 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_207'] = x_score_bollinger_bands_block__mutmut_207 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_208'] = x_score_bollinger_bands_block__mutmut_208 # type: ignore # mutmut generated
mutants_x_score_bollinger_bands_block__mutmut['x_score_bollinger_bands_block__mutmut_209'] = x_score_bollinger_bands_block__mutmut_209 # type: ignore # mutmut generated
