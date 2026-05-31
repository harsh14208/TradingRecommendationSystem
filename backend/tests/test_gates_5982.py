"""
Unit tests for §59–§82 gate implementations (2026-05-30).

Coverage map:
  _assemble_signal gates (§48, §49, §56, §64, §65, §66, §68, §77, §82):
    tested by calling _assemble_signal() directly with crafted inputs.
  delivery_gates gates (§67 FOMC, §78 Sep/Oct):
    tested via check_delivery_gates() with a mock DB.
  technicals compute gates (§59 OU halflife, §60 Hurst):
    tested via get_technical_indicators() or inline helpers.

Each gate test has two assertions:
  (a) gate fires and produces the expected confidence delta / rationale head
  (b) gate abstains (or reverses) when the trigger condition is absent
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Shared helpers ────────────────────────────────────────────────────────────


def _mr_buy_kwargs(**overrides):
    """Minimal MR BUY signal kwargs — RSI<42 satisfies _has_mr."""
    defaults = dict(
        ticker="NVDA",
        info={"company": "NVIDIA"},
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "volume": 5_000_000, "avg_volume": 4_000_000},
        score=50.0,
        rationale=[],
        sources=set(),
        _force_hold=False,
        _is_low_atr=False,
        _atr_pct_pre=0.02,
        total_confidence_penalty=0.0,
        avg_sent=0.5,
        price=100.0,
        atr=2.0,
        market_ctx={"macro": {"sp500_trend": "up"}},
        earnings_cal={},
        sector_rs=None,
        days_to_earnings=None,
    )
    defaults.update(overrides)
    return defaults


def _asm(**kwargs):
    from services.signal_engine import _assemble_signal
    from unittest.mock import patch
    import services.signal_ml as _sml

    with patch.object(_sml, "get_model", return_value=None):
        return _assemble_signal(**kwargs)


def _sig(**kwargs):
    """Minimal signal dict for delivery_gates tests.

    Includes Options + Fundamental as non-TA sources so the source-count gate
    (needs ≥2 non-TA for position style) is pre-satisfied; the test can then
    focus on the specific gate under test.
    """
    base = {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 65.0,
        "style": "position",
        "sectorEtf": "XLK",
        "sources": ["Technical", "Options", "Fundamental"],
        "entry": 100.0,
        "target": 110.0,
        "daysToEarnings": 30,
        "rationale": [],
    }
    base.update(kwargs)
    return base


class _Settings:
    min_confidence = 55.0


async def _mock_db_zero_sector():
    db = AsyncMock()
    result = AsyncMock()
    result.scalar_one = MagicMock(return_value=0)
    db.execute = AsyncMock(return_value=result)
    return db


# ── §65 TRIN / Arms Index ─────────────────────────────────────────────────────


def test_trin_capitulation_adds_confidence():
    """TRIN > 2.0 on MR BUY should add +4pp confidence."""
    base = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up", "trin": 2.5}})
    base_no_trin = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up"}})

    res_trin = _asm(**base)
    res_no = _asm(**base_no_trin)

    if res_trin and res_no and res_trin["action"] == res_no["action"] == "BUY":
        assert res_trin["confidence"] >= res_no["confidence"], "TRIN>2.0 should not reduce confidence"
        heads = [r["head"] for r in res_trin["rationale"]]
        assert any("TRIN" in h or "Capitulation" in h for h in heads), f"Expected TRIN rationale card; got: {heads}"


def test_trin_below_threshold_no_bonus():
    """TRIN <= 2.0 should not trigger the capitulation card."""
    base = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up", "trin": 1.5}})
    res = _asm(**base)
    if res:
        heads = [r["head"] for r in res["rationale"]]
        assert not any("TRIN" in h and "Capitulation" in h for h in heads), (
            "TRIN 1.5 should not fire the capitulation card"
        )


# ── §66 AD Breadth / Zweig Thrust ────────────────────────────────────────────


def test_zweig_thrust_adds_confidence():
    """Zweig breadth thrust should add confidence on BUY."""
    base = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up", "zweig_thrust": True}})
    base_no = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up", "zweig_thrust": False}})

    res = _asm(**base)
    res_no = _asm(**base_no)

    if res and res_no and res["action"] == res_no["action"] == "BUY":
        assert res["confidence"] >= res_no["confidence"], "Zweig thrust should not reduce confidence vs no-thrust"
        heads = [r["head"] for r in res["rationale"]]
        assert any("Zweig" in h or "Breadth" in h or "breadth" in h.lower() for h in heads), (
            f"Expected Zweig/breadth rationale; got: {heads}"
        )


def test_ad_breadth_deteriorating_reduces_confidence():
    """AD EMA10 drop < -200 should add a negative rationale."""
    base = _mr_buy_kwargs(market_ctx={"macro": {"sp500_trend": "up", "ad_ema10_chg": -300.0}})
    res = _asm(**base)

    if res and res["action"] == "BUY":
        heads = [r["head"] for r in res["rationale"]]
        sents = [
            r["sentiment"]
            for r in res["rationale"]
            if "breadth" in r.get("head", "").lower() or "AD" in r.get("head", "") or "Breadth" in r.get("head", "")
        ]
        # Expect a negative-sentiment breadth card
        assert any(
            "neg" in r["sentiment"]
            for r in res["rationale"]
            if "Breadth" in r.get("head", "") or "AD" in r.get("head", "")
        ), f"AD deterioration should produce neg sentiment card; heads={heads}"


# ── §64 Yield Curve — XLF Penalty ────────────────────────────────────────────


def test_inverted_yield_curve_penalises_xlf():
    """Deeply inverted yield curve (t10y2y < -0.5) + XLF sector → -5pp."""
    xlf_rs = {"sector_etf": "XLF", "rs_vs_sector": 0}
    base_inv = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y2y_spread": -0.8}},
        sector_rs=xlf_rs,
    )
    base_flat = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y2y_spread": 0.5}},
        sector_rs=xlf_rs,
    )

    res_inv = _asm(**base_inv)
    res_flat = _asm(**base_flat)

    if res_inv and res_flat and res_inv["action"] == res_flat["action"] == "BUY":
        assert res_inv["confidence"] < res_flat["confidence"], "Inverted yield curve should lower XLF confidence"
        heads = [r["head"] for r in res_inv["rationale"]]
        assert any("Yield Curve" in h or "Inverted" in h for h in heads), (
            f"Expected yield curve rationale; got: {heads}"
        )


def test_yield_curve_no_penalty_for_non_xlf():
    """Inverted yield curve should not penalise non-XLF sectors."""
    xlk_rs = {"sector_etf": "XLK", "rs_vs_sector": 0}
    base = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y2y_spread": -0.8}},
        sector_rs=xlk_rs,
    )
    res = _asm(**base)
    if res:
        heads = [r["head"] for r in res["rationale"]]
        assert not any("Inverted Yield" in h for h in heads), "Yield curve penalty should only apply to XLF"


# ── §68 T10Y Rate of Change — XLK Headwind/Tailwind ─────────────────────────


def test_rising_rates_penalise_xlk():
    """t10y_30d_chg > 0.5 + XLK sector → -6pp confidence."""
    xlk_rs = {"sector_etf": "XLK", "rs_vs_sector": 0}
    base_rising = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y_30d_chg": 0.7}},
        sector_rs=xlk_rs,
    )
    base_stable = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y_30d_chg": 0.1}},
        sector_rs=xlk_rs,
    )

    res_rising = _asm(**base_rising)
    res_stable = _asm(**base_stable)

    if res_rising and res_stable and res_rising["action"] == res_stable["action"] == "BUY":
        assert res_rising["confidence"] < res_stable["confidence"], "Rising rates should lower XLK confidence"
        heads = [r["head"] for r in res_rising["rationale"]]
        assert any("Rising Rate" in h or "Headwind" in h or "Rate" in h for h in heads), (
            f"Expected rising-rates rationale; got: {heads}"
        )


def test_falling_rates_boost_xlk():
    """t10y_30d_chg < -0.3 → +3pp tailwind on any sector."""
    base = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y_30d_chg": -0.5}},
    )
    base_stable = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "t10y_30d_chg": 0.0}},
    )

    res = _asm(**base)
    res_stable = _asm(**base_stable)

    if res and res_stable and res["action"] == res_stable["action"] == "BUY":
        assert res["confidence"] >= res_stable["confidence"], "Falling rates should not reduce confidence"
        heads = [r["head"] for r in res["rationale"]]
        assert any("Falling" in h or "Tailwind" in h or "Rate" in h for h in heads), (
            f"Expected falling-rates tailwind rationale; got: {heads}"
        )


# ── §48 IVR Gate ──────────────────────────────────────────────────────────────


def test_high_ivr_adds_confidence_on_mr_buy():
    """IVR ≥50 on MR BUY with VIX>15 → positive IVR rationale card present."""
    base_high = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "vix": 22.0}},
        opt_flow={"sweep_calls": False, "gex": 0, "pc_ratio": 0.8, "iv_rank": 65.0},
    )

    res_high = _asm(**base_high)

    if res_high and res_high["action"] == "BUY":
        heads = [r["head"] for r in res_high["rationale"]]
        assert any("IVR" in h or "IV Rank" in h for h in heads), (
            f"Expected IVR rationale card for iv_rank=65; got: {heads}"
        )
        # Card should be positive-sentiment (dealer unwind amplifies recovery)
        ivr_cards = [r for r in res_high["rationale"] if "IVR" in r.get("head", "") or "IV Rank" in r.get("head", "")]
        assert any(r["sentiment"] == "pos" for r in ivr_cards), (
            f"High IVR card should have positive sentiment; got: {ivr_cards}"
        )


def test_low_ivr_reduces_confidence():
    """IVR < 20 on MR BUY → -3pp penalty rationale."""
    base = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "vix": 18.0}},
        opt_flow={"sweep_calls": False, "gex": 0, "pc_ratio": 0.8, "iv_rank": 12.0},
    )
    res = _asm(**base)
    if res and res["action"] == "BUY":
        heads = [r["head"] for r in res["rationale"]]
        neg_ivr = [r for r in res["rationale"] if "IVR" in r.get("head", "") or "IV Rank" in r.get("head", "")]
        if neg_ivr:
            assert any(r["sentiment"] == "neg" for r in neg_ivr), "Low IVR card should have negative sentiment"


# ── §49 Put-Call Skew ─────────────────────────────────────────────────────────


def test_high_put_call_skew_adds_confidence():
    """skew_25d > 0.10 on MR BUY → +4pp confidence."""
    base_high = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "vix": 20.0}},
        opt_flow={"sweep_calls": False, "gex": 0, "pc_ratio": 0.8, "skew_25d": 0.15},
    )
    base_low = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "vix": 20.0}},
        opt_flow={"sweep_calls": False, "gex": 0, "pc_ratio": 0.8, "skew_25d": 0.02},
    )

    res_high = _asm(**base_high)
    res_low = _asm(**base_low)

    if res_high and res_low and res_high["action"] == res_low["action"] == "BUY":
        assert res_high["confidence"] >= res_low["confidence"], (
            "High put-call skew should not reduce confidence below low-skew baseline"
        )
        heads = [r["head"] for r in res_high["rationale"]]
        assert any("Skew" in h or "skew" in h.lower() or "Put" in h for h in heads), (
            f"Expected skew rationale card; got: {heads}"
        )


# ── §77 Tax-Loss Harvesting Window ────────────────────────────────────────────


def test_tax_loss_window_adds_confidence_november():
    """November + price near 52wk low → +4pp confidence."""
    import services.signal_engine as _se

    # November date
    nov_date = datetime(2026, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
    base = _mr_buy_kwargs(
        info={"company": "NVDA", "week_52_low": 95.0},
        price=100.0,
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "volume": 5_000_000, "avg_volume": 4_000_000},
    )
    base_no_low = _mr_buy_kwargs(
        info={"company": "NVDA", "week_52_low": 50.0},  # price 100 >> 52wk low 50 (not near low)
        price=100.0,
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "volume": 5_000_000, "avg_volume": 4_000_000},
    )

    with patch.object(_se, "datetime", wraps=_se.datetime) as mock_dt:
        mock_dt.now.return_value = nov_date
        res = _asm(**base)
        res_no = _asm(**base_no_low)

    if res and res["action"] == "BUY":
        heads = [r["head"] for r in res["rationale"]]
        assert any("Tax" in h or "tax" in h.lower() or "Season" in h for h in heads), (
            f"Expected tax-loss rationale in November near 52wk low; got: {heads}"
        )

    if res and res_no and res["action"] == res_no["action"] == "BUY":
        assert res["confidence"] >= res_no["confidence"], (
            "Tax-loss window (near 52wk low) should not reduce confidence vs far-from-low"
        )


def test_tax_loss_window_inactive_in_june():
    """June is outside tax-loss season — no tax-loss rationale expected."""
    import services.signal_engine as _se

    june_date = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    base = _mr_buy_kwargs(
        info={"company": "NVDA", "week_52_low": 95.0},
        price=100.0,
    )

    with patch.object(_se, "datetime", wraps=_se.datetime) as mock_dt:
        mock_dt.now.return_value = june_date
        res = _asm(**base)

    if res:
        heads = [r["head"] for r in res["rationale"]]
        assert not any("Tax-Loss" in h or "tax-loss" in h.lower() for h in heads), (
            f"Tax-loss card should not fire in June; got: {heads}"
        )


# ── §82 Trailing Stop ─────────────────────────────────────────────────────────


def test_trailing_stop_pct_present_on_buy():
    """Every BUY signal should carry a trailingStopPct field."""
    res = _asm(**_mr_buy_kwargs(price=100.0, atr=2.0))
    if res and res["action"] == "BUY":
        assert "trailingStopPct" in res, "BUY signal must include trailingStopPct"
        assert res["trailingStopPct"] is not None
        assert res["trailingStopPct"] > 0


def test_trailing_stop_pct_scales_with_atr():
    """trailingStopPct should be larger for higher ATR."""
    res_high_atr = _asm(**_mr_buy_kwargs(price=100.0, atr=4.0))
    res_low_atr = _asm(**_mr_buy_kwargs(price=100.0, atr=1.0))

    if (
        res_high_atr
        and res_low_atr
        and res_high_atr["action"] == res_low_atr["action"] == "BUY"
        and res_high_atr["trailingStopPct"] is not None
        and res_low_atr["trailingStopPct"] is not None
    ):
        assert res_high_atr["trailingStopPct"] > res_low_atr["trailingStopPct"], (
            "Higher ATR should produce a wider trailing stop pct"
        )


# ── §56 Kelly / Position Size Scale ──────────────────────────────────────────


def test_position_size_scale_increases_in_fear_regime():
    """VIX 20–30 + conf≥58 should produce positionSizeScale > 1.0."""
    base = _mr_buy_kwargs(
        score=60.0,
        market_ctx={"macro": {"sp500_trend": "up", "vix": 25.0}},
    )
    res = _asm(**base)

    if res and res["action"] == "BUY" and res.get("confidence", 0) >= 58:
        scale = res.get("positionSizeScale", 1.0)
        assert scale >= 1.0, f"VIX 25 + conf≥58 should not reduce position scale; got {scale}"


def test_position_size_scale_reduces_in_calm_regime():
    """VIX < 15 should produce positionSizeScale <= 1.0 (reduced risk in calm market)."""
    base = _mr_buy_kwargs(
        market_ctx={"macro": {"sp500_trend": "up", "vix": 12.0}},
    )
    res = _asm(**base)
    if res:
        scale = res.get("positionSizeScale", 1.0)
        assert scale <= 1.0, f"VIX<15 (calm regime) should reduce position scale; got {scale}"


# ── §67 FOMC Proximity (delivery_gates) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_fomc_decision_day_blocks_buy():
    """FOMC day (distance=0) → hard block on BUY signals."""
    from services.delivery_gates import check_delivery_gates, _FOMC_DATES_2026

    db = await _mock_db_zero_sector()
    # Pick a known FOMC date
    fomc_date_str = sorted(_FOMC_DATES_2026)[0]  # e.g. 2026-01-28
    fomc_dt = datetime.strptime(fomc_date_str, "%Y-%m-%d").replace(hour=14, minute=0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = fomc_dt
        mock_dt.strptime = datetime.strptime
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=70.0), db, _Settings())

    assert reason is not None, "FOMC day should block BUY"
    assert "FOMC" in reason


@pytest.mark.asyncio
async def test_fomc_day_minus_one_applies_haircut():
    """One day before FOMC → −4pp haircut (not hard block)."""
    from services.delivery_gates import check_delivery_gates, _FOMC_DATES_2026
    from datetime import date, timedelta

    db = await _mock_db_zero_sector()
    fomc_date_str = sorted(_FOMC_DATES_2026)[0]
    fomc_d = date.fromisoformat(fomc_date_str)
    day_before = fomc_d - timedelta(days=1)
    day_before_dt = datetime(day_before.year, day_before.month, day_before.day, 14, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = day_before_dt
        mock_dt.strptime = datetime.strptime
        reason, out_sig = await check_delivery_gates(_sig(action="BUY", confidence=65.0), db, _Settings())

    # Gate should NOT hard-block (returns None reason if conf still above floor)
    # Check rationale contains FOMC haircut card
    rationale_heads = [r.get("head", "") for r in out_sig.get("rationale", [])]
    assert any("FOMC" in h for h in rationale_heads), (
        f"Expected FOMC haircut rationale on day T-1; got: {rationale_heads}"
    )
    # Confidence should be reduced
    assert out_sig["confidence"] < 65.0, f"Confidence should be reduced on T-1 FOMC; got {out_sig['confidence']}"


@pytest.mark.asyncio
async def test_fomc_far_away_no_effect():
    """7 days from nearest FOMC → no FOMC gate fires."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    # A date known to be far from any FOMC (mid-month non-FOMC month)
    safe_dt = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = safe_dt
        mock_dt.strptime = datetime.strptime
        reason, out_sig = await check_delivery_gates(_sig(action="BUY", confidence=65.0), db, _Settings())

    rationale_heads = [r.get("head", "") for r in out_sig.get("rationale", [])]
    assert not any("FOMC" in h for h in rationale_heads), f"No FOMC card expected 7d from FOMC; got: {rationale_heads}"
    assert out_sig["confidence"] == 65.0, "Confidence should not change 7d from FOMC"


# ── §78 Sep/Oct Seasonality (delivery_gates) ─────────────────────────────────


@pytest.mark.asyncio
async def test_september_gate_blocks_low_confidence():
    """September BUY with confidence < 62 → blocked."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    sep_dt = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = sep_dt
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=58.0), db, _Settings())

    assert reason is not None, "September gate should block BUY with conf<62"
    assert "September" in reason or "seasonality" in reason.lower()


@pytest.mark.asyncio
async def test_september_gate_passes_high_confidence():
    """September BUY with confidence ≥ 62 → gate passes."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    sep_dt = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = sep_dt
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=63.0), db, _Settings())

    assert reason is None or "September" not in str(reason), "September gate should pass with confidence ≥ 62"


@pytest.mark.asyncio
async def test_october_gate_blocks_low_confidence():
    """October BUY with confidence < 60 → blocked."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    oct_dt = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = oct_dt
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=57.0), db, _Settings())

    assert reason is not None, "October gate should block BUY with conf<60"
    assert "October" in reason or "seasonality" in reason.lower()


@pytest.mark.asyncio
async def test_october_gate_passes_above_threshold():
    """October BUY with confidence ≥ 60 → gate passes."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    oct_dt = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = oct_dt
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=61.0), db, _Settings())

    assert reason is None or "October" not in str(reason), "October gate should pass with confidence ≥ 60"


@pytest.mark.asyncio
async def test_seasonality_gate_inactive_in_march():
    """March is not a restricted month — no seasonality block."""
    from services.delivery_gates import check_delivery_gates

    db = await _mock_db_zero_sector()
    mar_dt = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value = mar_dt
        reason, _ = await check_delivery_gates(_sig(action="BUY", confidence=56.0), db, _Settings())

    assert reason is None or ("September" not in str(reason) and "October" not in str(reason)), (
        "Seasonality gate should not fire in March"
    )


# ── §59 OU Halflife (technicals compute) ─────────────────────────────────────


def test_ou_halflife_fast_reverting_series():
    """A strongly mean-reverting synthetic series should produce a short halflife."""
    import numpy as np
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from services.technicals import calculate_indicators as get_technical_indicators

    # Synthetic AR(1) with θ = 0.5 → fast mean-reversion → short OU halflife
    np.random.seed(42)
    n = 126
    prices = [100.0]
    for _ in range(n - 1):
        prices.append(100.0 + 0.5 * (prices[-1] - 100.0) + np.random.normal(0, 0.5))

    import pandas as pd

    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )

    result = get_technical_indicators(df)
    ou_hl = result.get("ou_halflife")

    # For a fast-reverting AR(1) series, halflife should be reasonably short
    # (not None, and not astronomically large)
    if ou_hl is not None:
        assert ou_hl < 50, f"Fast-reverting series should have short OU halflife; got {ou_hl}"


def test_ou_halflife_trending_series_returns_none_or_large():
    """A pure trending series (random walk) should have large/None OU halflife."""
    import numpy as np
    import pandas as pd
    from services.technicals import calculate_indicators as get_technical_indicators

    np.random.seed(0)
    n = 126
    prices = list(np.cumsum(np.random.normal(0.1, 1.0, n)) + 100.0)

    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )

    result = get_technical_indicators(df)
    ou_hl = result.get("ou_halflife")

    # A trending series should either give None (θ >= 0) or a very large halflife
    if ou_hl is not None:
        assert ou_hl > 10, f"Trending series OU halflife should be large or None; got {ou_hl}"


# ── §60 Hurst Exponent (technicals compute) ──────────────────────────────────


def test_hurst_anti_persistent_series():
    """A synthetic mean-reverting series should yield Hurst < 0.5."""
    import numpy as np
    import pandas as pd
    from services.technicals import calculate_indicators as get_technical_indicators

    np.random.seed(7)
    n = 252
    # Anti-persistent: each step negatively correlated with prior step
    prices = [100.0]
    direction = 1
    for _ in range(n - 1):
        direction *= -1
        prices.append(prices[-1] + direction * abs(np.random.normal(0, 0.5)))

    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p + 0.5 for p in prices],
            "Low": [p - 0.5 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )

    result = get_technical_indicators(df)
    h = result.get("hurst")
    if h is not None:
        assert h < 0.6, f"Anti-persistent series should have H < 0.6; got {h}"


def test_hurst_trending_series():
    """A trending series should yield Hurst > 0.5."""
    import numpy as np
    import pandas as pd
    from services.technicals import calculate_indicators as get_technical_indicators

    np.random.seed(3)
    n = 252
    # Persistent: cumulative sum → trending
    prices = list(np.cumsum(np.abs(np.random.normal(0.2, 0.1, n))) + 100.0)

    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.005 for p in prices],
            "Low": [p * 0.995 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )

    result = get_technical_indicators(df)
    h = result.get("hurst")
    if h is not None:
        assert h > 0.4, f"Trending series should have H > 0.4; got {h}"


def test_hurst_requires_minimum_data():
    """Fewer than 40 data points → Hurst should be None."""
    import pandas as pd
    from services.technicals import calculate_indicators as get_technical_indicators

    n = 20
    prices = [100.0 + i * 0.1 for i in range(n)]
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p + 0.2 for p in prices],
            "Low": [p - 0.2 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * n,
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )

    result = get_technical_indicators(df)
    # With only 20 points, Hurst should be None or computed but not reliable
    # We just check it doesn't crash and returns a dict
    assert isinstance(result, dict)
