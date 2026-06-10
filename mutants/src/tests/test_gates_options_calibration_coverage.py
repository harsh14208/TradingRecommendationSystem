"""Unit tests for gates/options.py class gates and calibration.apply_calibration."""

from services.gates.base import SignalContext
from services.gates.options import (
    IvrMrGate,
    IvTermStructureGate,
    OptionsFlowConfirmationGate,
    PutCallSkewGate,
    PutSweepCapitulationGate,
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


# ── OptionsFlowConfirmationGate ──────────────────────────────────────────────


def test_options_flow_extreme_put_blocks():
    ctx = _ctx(opt_flow={"pc_ratio": 2.5})
    OptionsFlowConfirmationGate().apply(ctx)
    assert ctx.action == "HOLD"


def test_options_flow_sweep_plus_gex_boost():
    ctx = _ctx(opt_flow={"sweep_calls": [{"x": 1}], "gex": 5e6})
    before = ctx.confidence
    OptionsFlowConfirmationGate().apply(ctx)
    assert ctx.confidence == round(before + 15, 1)


def test_options_flow_standard_confirmation_boost():
    ctx = _ctx(opt_flow={"pc_ratio": 0.5, "gex": 2e6})
    before = ctx.confidence
    OptionsFlowConfirmationGate().apply(ctx)
    assert ctx.confidence == round(before + 5, 1)


def test_options_flow_unconfirmed_haircut():
    ctx = _ctx(opt_flow={"pc_ratio": 1.6, "gex": -2e6})
    before = ctx.confidence
    OptionsFlowConfirmationGate().apply(ctx)
    assert ctx.confidence == round(before - 5, 1)


def test_options_flow_skips_without_opt_flow():
    ctx = _ctx(opt_flow=None)
    OptionsFlowConfirmationGate().apply(ctx)
    assert ctx.action == "BUY" and ctx.confidence == 60.0


# ── IvrMrGate (modifies score) ───────────────────────────────────────────────


def test_ivr_mr_high_boost():
    ctx = _ctx(vix=22.0, opt_flow={"iv_rank": 60})
    IvrMrGate().apply(ctx)
    assert ctx.score == 55.0  # +5


def test_ivr_mr_low_penalty():
    ctx = _ctx(vix=22.0, opt_flow={"iv_rank": 10})
    IvrMrGate().apply(ctx)
    assert ctx.score == 47.0  # -3


def test_ivr_mr_skips_low_vix():
    ctx = _ctx(vix=12.0, opt_flow={"iv_rank": 60})
    IvrMrGate().apply(ctx)
    assert ctx.score == 50.0  # vix<=15 → skipped


# ── PutCallSkewGate / IvTermStructureGate / PutSweepCapitulationGate ─────────


def test_put_call_skew_boost():
    ctx = _ctx(opt_flow={"skew_25d": 0.15})
    PutCallSkewGate().apply(ctx)
    assert ctx.score == 54.0  # +4


def test_iv_term_structure_boost():
    ctx = _ctx(opt_flow={"iv_term_spike": 2.0})
    IvTermStructureGate().apply(ctx)
    assert ctx.score == 54.0  # +4


def test_iv_term_structure_skips_low_spike():
    ctx = _ctx(opt_flow={"iv_term_spike": 1.2})
    IvTermStructureGate().apply(ctx)
    assert ctx.score == 50.0  # <=1.5 → skip


def test_put_sweep_capitulation_boost():
    ctx = _ctx(opt_flow={"sweep_puts": [{"vol_oi": 15, "vol": 2000}], "sweep_calls": []})
    before = ctx.confidence
    PutSweepCapitulationGate().apply(ctx)
    assert ctx.confidence == round(before + 5, 1)


def test_put_sweep_skipped_when_calls_present():
    ctx = _ctx(opt_flow={"sweep_puts": [{"vol_oi": 15, "vol": 2000}], "sweep_calls": [{"x": 1}]})
    PutSweepCapitulationGate().apply(ctx)
    assert ctx.confidence == 60.0


# ── calibration.apply_calibration (pure) ─────────────────────────────────────


def test_apply_calibration_no_map_returns_raw():
    from services.calibration import apply_calibration

    assert apply_calibration(60.0, "BUY", {}) == (60.0, None)


def test_apply_calibration_hold_action_returns_raw():
    from services.calibration import apply_calibration

    cal, meta = apply_calibration(60.0, "HOLD", {"_isotonic": [[i / 9, i / 9] for i in range(10)]})
    assert cal == 60.0 and meta is None


def test_apply_calibration_isotonic_global():
    from services.calibration import apply_calibration

    iso = [[i / 9.0, i / 9.0] for i in range(10)]  # identity isotonic, 10 points
    cal, meta = apply_calibration(55.0, "BUY", {"_isotonic": iso})
    assert isinstance(cal, float)
    assert meta is not None and meta["source"] == "isotonic_global"


def test_apply_calibration_platt_bin_blend():
    from services.calibration import apply_calibration

    # No isotonic → Platt bin fallback. Bin keyed by raw//_BIN_SIZE.
    cal_map = {"50": {"win_rate": 0.62, "blend": 0.5}, "55": {"win_rate": 0.62, "blend": 0.5}}
    cal, meta = apply_calibration(55.0, "BUY", cal_map)
    assert isinstance(cal, float)
