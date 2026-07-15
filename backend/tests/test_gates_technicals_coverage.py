"""Unit tests for gates/technicals.py — class-based GateBase gates.

Each test builds a SignalContext via _ctx() and asserts the HOLD/penalty trigger.
"""

from services.gates.base import SignalContext
from services.gates.technicals import (
    AtrRankCeilingGate,
    AtrRankFloorGate,
    BearHighVixGate,
    DeepBearRsiGate,
    GlobalVixMinGate,
    Max21Gate,
    MrEntryConditionGate,
    MrPersistenceGate,
    NearEarningsCautionGate,
    ReturnJumpGate,
    SectorVixFloorGate,
    SellUptrendGate,
    Sma200BuyGate,
    SpyNeutralZoneGate,
    StlfsiVixGate,
    VixDirectionGate,
)


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
        vix=22.0,
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
        sector_config={},
    )
    base.update(over)
    return SignalContext(**base)


def test_stlfsi_vix_stress_regime_blocks():
    ctx = _ctx(macro={"stlfsi": 2.0}, vix=35.0)
    StlfsiVixGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_stlfsi_vix_elevated_marginal_blocks():
    ctx = _ctx(macro={"stlfsi": 1.2}, vix=27.0, score=40.0)
    StlfsiVixGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_stlfsi_vix_no_data_passes():
    ctx = _ctx(macro={}, vix=None)
    StlfsiVixGate().apply(ctx)
    assert ctx.action == "BUY"


def test_global_vix_min_blocks_low_fear():
    ctx = _ctx(vix=15.0, has_mr=True)
    GlobalVixMinGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_global_vix_min_passes_high_vix():
    ctx = _ctx(vix=25.0, has_mr=True)
    GlobalVixMinGate().apply(ctx)
    assert ctx.action == "BUY"


def test_sma200_buy_gate_blocks_downtrend():
    ctx = _ctx(price=95.0, score=50.0, tech={"sma200": 100.0, "rsi": 30})
    Sma200BuyGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_sma200_buy_gate_passes_above_ma():
    ctx = _ctx(price=105.0, score=50.0, tech={"sma200": 100.0, "rsi": 30})
    Sma200BuyGate().apply(ctx)
    assert ctx.action == "BUY"


def test_sell_uptrend_gate_blocks_without_altdata():
    ctx = _ctx(action="SELL", price=105.0, score=0.0, tech={"sma200": 100.0}, sources=set())
    SellUptrendGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_sell_uptrend_gate_passes_with_altdata():
    ctx = _ctx(action="SELL", price=105.0, score=0.0, tech={"sma200": 100.0}, sources={"Options"})
    SellUptrendGate().apply(ctx)
    assert ctx.action == "SELL"


def test_spy_neutral_zone_blocks_marginal():
    ctx = _ctx(score=40.0, macro={"sp500_neutral_zone": True, "sp500_sma200_ratio": 1.0})
    SpyNeutralZoneGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_bear_high_vix_blocks():
    ctx = _ctx(sp500_trend="down", vix=30.0, score=40.0)
    BearHighVixGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_mr_persistence_gate_haircut():
    ctx = _ctx(tech={"momentum_ar1": 0.5}, has_mr=True, info={"revenue_growth": -0.1})
    before = ctx.confidence
    MrPersistenceGate().apply(ctx)
    assert ctx.confidence <= before  # AR(1) momentum penalty (or no-op)


def test_mr_entry_condition_blocks_no_mr():
    ctx = _ctx(has_mr=False, score=50.0, tech={})
    MrEntryConditionGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_atr_rank_floor_blocks_dormant():
    ctx = _ctx(has_mr=True, tech={"atr_pct_rank": 10}, sector_config={"atr_rank_min": 20})
    AtrRankFloorGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_sector_vix_floor_blocks():
    ctx = _ctx(has_mr=True, vix=18.0, sector_config={"vix_min": 25})
    SectorVixFloorGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_atr_rank_ceiling_blocks_trending_panic():
    ctx = _ctx(has_mr=True, vix=25.0, tech={"atr_pct_rank": 85})
    AtrRankCeilingGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_return_jump_gate_blocks_large_drop():
    ctx = _ctx(has_mr=True, tech={"change_pct": -8.0})
    ReturnJumpGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_vix_direction_gate_blocks_rising_vix():
    ctx = _ctx(has_mr=True, vix=18.0, macro={"vix_3d_slope": 4.0})
    VixDirectionGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_near_earnings_caution_haircut():
    ctx = _ctx(days_to_earnings=10, opt_flow={}, info={})
    before = ctx.confidence
    NearEarningsCautionGate().apply(ctx)
    assert ctx.confidence < before  # -2 or -3 pp


def test_deep_bear_rsi_gate_blocks():
    ctx = _ctx(vix=30.0, macro={"sp500_sma200_ratio": 0.90}, tech={"rsi": 40, "sma200": 100})
    DeepBearRsiGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_max21_gate_blocks_high_max():
    ctx = _ctx(has_mr=True, tech={"max_21": 5.0, "max_21_median": 2.5})
    Max21Gate().apply(ctx)
    assert ctx.action == "HOLD"
    assert any(r["src"] == "Risk Gate" for r in ctx.rationale)


def test_max21_gate_passes_low_max():
    ctx = _ctx(has_mr=True, tech={"max_21": 1.5, "max_21_median": 2.5})
    Max21Gate().apply(ctx)
    assert ctx.action == "BUY"


def test_max21_gate_no_data_passes():
    ctx = _ctx(has_mr=True, tech={})
    Max21Gate().apply(ctx)
    assert ctx.action == "BUY"


def test_max21_gate_ignores_non_buy():
    ctx = _ctx(action="SELL", has_mr=True, tech={"max_21": 5.0, "max_21_median": 2.5})
    Max21Gate().apply(ctx)
    assert ctx.action == "SELL"
