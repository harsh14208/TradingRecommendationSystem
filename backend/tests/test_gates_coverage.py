"""Unit tests for the gate modules (volume, calendar, fundamentals).

Function-based gates are called directly; class-based gates are exercised via a
SignalContext built by the _ctx() factory.
"""

from services.gates.base import SignalContext
from services.gates.calendar import CalendarGate, apply_calendar_gates
from services.gates.fundamentals import (
    apply_quality_screens,
    apply_short_interest_velocity,
)
from services.gates.volume import AdxGate, DollarVolumeGate, OverboughtWeakTrendGate, RvolGate


def _ctx(**over) -> SignalContext:
    base = dict(
        action="BUY",
        confidence=60.0,
        score=50.0,
        rationale=[],
        sources=set(),
        ticker="AAPL",
        tech={},
        info={},
        macro={},
        price=100.0,
        atr=2.0,
        has_mr=True,
        vix=18.0,
        sp500_trend="up",
        sector_etf="XLK",
        today_dow=2,
        month=6,
        opt_flow=None,
        sector_rs=None,
        earnings_cal={},
        days_to_earnings=None,
        is_low_atr=False,
        atr_pct_pre=0.03,
    )
    base.update(over)
    return SignalContext(**base)


# ── RvolGate ─────────────────────────────────────────────────────────────────


def test_rvol_gate_blocks_low_volume():
    ctx = _ctx(tech={"volume": 100, "avg_volume": 1000, "rsi": 45, "adr_compression": True})
    RvolGate().apply(ctx)
    assert ctx.action == "HOLD"
    assert any("RVOL" in c["head"] for c in ctx.rationale)


def test_rvol_gate_oversold_waiver():
    ctx = _ctx(tech={"volume": 100, "avg_volume": 1000, "rsi": 25})
    RvolGate().apply(ctx)
    assert ctx.action == "BUY"  # RSI<30 waiver


def test_rvol_gate_sufficient_volume_passes():
    ctx = _ctx(tech={"volume": 2000, "avg_volume": 1000, "rsi": 45})
    RvolGate().apply(ctx)
    assert ctx.action == "BUY"


def test_rvol_gate_skips_when_not_buy_or_no_data():
    ctx = _ctx(action="SELL", tech={"volume": 1, "avg_volume": 1000})
    RvolGate().apply(ctx)
    assert ctx.action == "SELL"
    ctx2 = _ctx(tech={"volume": 1, "avg_volume": 0})
    RvolGate().apply(ctx2)
    assert ctx2.action == "BUY"  # no avg_volume → skipped


# ── AdxGate ──────────────────────────────────────────────────────────────────


def test_adx_gate_blocks_directionless():
    ctx = _ctx(score=40.0, tech={"adx": 12, "rsi": 45})
    AdxGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_adx_gate_skips_when_no_adx_or_strong():
    ctx = _ctx(score=40.0, tech={"rsi": 45})  # adx None
    AdxGate().apply(ctx)
    assert ctx.action == "BUY"
    ctx2 = _ctx(score=40.0, tech={"adx": 25, "rsi": 45})
    AdxGate().apply(ctx2)
    assert ctx2.action == "BUY"


# ── OverboughtWeakTrendGate ──────────────────────────────────────────────────


def test_overbought_weak_trend_blocks():
    ctx = _ctx(score=35.0, sp500_trend="up", tech={"rsi": 75, "adx": 20})
    OverboughtWeakTrendGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_overbought_strong_trend_passes():
    ctx = _ctx(score=35.0, sp500_trend="up", tech={"rsi": 75, "adx": 30})
    OverboughtWeakTrendGate().apply(ctx)
    assert ctx.action == "BUY"  # ADX≥28 → continuation


# ── DollarVolumeGate ─────────────────────────────────────────────────────────


def test_dollar_volume_haircut_and_low_atr():
    # $0.5M/day → 8pp haircut; low_atr disclosure also fires
    ctx = _ctx(price=10.0, tech={"volume": 50_000}, is_low_atr=True, atr_pct_pre=0.01)
    before = ctx.confidence
    DollarVolumeGate().apply(ctx)
    assert ctx.confidence == round(before - 8, 1)
    assert any("Thin Dollar Volume" in c["head"] for c in ctx.rationale)
    assert any("Low-ATR Regime" in c["head"] for c in ctx.rationale)


def test_dollar_volume_mid_haircut():
    # $3M/day → 4pp haircut
    ctx = _ctx(price=10.0, tech={"volume": 300_000})
    before = ctx.confidence
    DollarVolumeGate().apply(ctx)
    assert ctx.confidence == round(before - 4, 1)


# ── apply_calendar_gates (function) + CalendarGate (wrapper) ─────────────────


def test_calendar_friday_no_longer_blocks():
    # §57 Friday HOLD-flip removed 2026-07-14 (gate audit — unvalidated);
    # Friday low-score BUYs now pass through unchanged.
    action, conf, cards, srcs = apply_calendar_gates(
        action="BUY", confidence=60.0, score=50.0, today_dow=4, month=6, price=100.0, info={}
    )
    assert action == "BUY"
    assert cards == []


def test_calendar_near_52wk_low_hard_block():
    # §77 strengthened penalty→hard block 2026-07-14 (corrected-book audit:
    # −4pp cohort still resolved at ΔWR −16.4pp / negative net EV)
    action, conf, cards, _ = apply_calendar_gates(
        action="BUY",
        confidence=60.0,
        score=55.0,
        today_dow=2,
        month=6,
        price=100.0,
        info={"week_52_low": 95.0},  # price within 8% of low
    )
    assert action == "HOLD"
    assert conf == 60.0  # confidence untouched — the block is on action


def test_calendar_gate_wrapper_mutates_ctx():
    # §77 path: near 52-wk low hard-blocks via the wrapper.
    ctx = _ctx(today_dow=1, score=50.0, price=100.0, info={"week_52_low": 95.0}, confidence=60.0)
    CalendarGate().apply(ctx)
    assert ctx.action == "HOLD"
    assert repr(CalendarGate()) == "CalendarGate"


# ── apply_short_interest_velocity ────────────────────────────────────────────


def test_si_velocity_covering_bonus():
    score, cards, srcs = apply_short_interest_velocity(
        score=30.0,
        info={"shares_short": 80, "shares_short_prior": 100},  # -20% → covering
    )
    assert score == 34.0
    assert "Short Interest" in srcs


def test_si_velocity_adding_penalty():
    score, _, _ = apply_short_interest_velocity(
        score=30.0,
        info={"shares_short": 130, "shares_short_prior": 100},  # +30% → adding
    )
    assert score == 25.0


def test_si_velocity_missing_data():
    score, cards, srcs = apply_short_interest_velocity(score=30.0, info={})
    assert score == 30.0 and cards == [] and srcs == set()


# apply_insider_clustering tests removed 2026-07-14 (§73 deleted — 0 fires ever)

# ── apply_quality_screens (Piotroski branch) ─────────────────────────────────


def test_quality_screens_piotroski_strong():
    score, cards, srcs = apply_quality_screens(
        score=50.0, info={}, fundamentals={"piotroski_f": 8}, is_lev_etf=False, action="BUY"
    )
    assert score == 62.0  # +12
    assert "Fundamentals" in srcs


def test_quality_screens_no_fundamentals_is_noop():
    score, cards, srcs = apply_quality_screens(score=50.0, info={}, fundamentals={}, is_lev_etf=False, action="BUY")
    assert score == 50.0


# score_macro_extensions tests removed with gates/macro_extensions.py
# (gate audit 2026-07-14: 0 fires in 87,982 all-time signals — dead module)
