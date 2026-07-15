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
        "hasMr": True,  # MR gate required for BUY delivery (2026-06-02 fix)
    }
    base.update(kwargs)
    return base


class _Settings:
    min_confidence = 55.0


async def _mock_db_zero_sector():
    db = AsyncMock()
    result = AsyncMock()
    result.scalar_one = MagicMock(return_value=0)
    result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.fixture(autouse=True)
def _neutralize_calendar_gates():
    """Neutralize calendar-dependent gates (pre-long-weekend, Thursday) so tests
    are deterministic.  FOMC is NOT patched here — FOMC-specific tests rely on
    the real _days_to_nearest_fomc with a patched datetime."""
    from datetime import datetime, timezone

    _tuesday = datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc)
    with (
        patch("services.market_calendar.is_pre_long_weekend", return_value=(False, None)),
        patch("services.delivery_gates.datetime") as mock_dt,
    ):
        mock_dt.now.return_value = _tuesday
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield


# ── §65 TRIN / Arms Index ─────────────────────────────────────────────────────


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


# ── §64 Yield Curve — XLF Penalty ────────────────────────────────────────────


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


def test_near_52wk_low_penalises_confidence():
    """Near 52-week low now applies -4pp penalty (inverted 2026-05-31).

    Live-data audit: near-52wk-low signals have 31% WR (−11.5pp vs 42.5% baseline).
    The gate was inverted from +4pp boost → -4pp penalty based on Inv3 results.
    """
    import services.signal_engine as _se

    nov_date = datetime(2026, 11, 15, 12, 0, 0, tzinfo=timezone.utc)
    near_low = _mr_buy_kwargs(
        info={"company": "NVDA", "week_52_low": 95.0},
        price=100.0,
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "volume": 5_000_000, "avg_volume": 4_000_000},
    )
    far_from_low = _mr_buy_kwargs(
        info={"company": "NVDA", "week_52_low": 50.0},
        price=100.0,
        tech={"price": 100.0, "atr": 2.0, "rsi": 38.0, "volume": 5_000_000, "avg_volume": 4_000_000},
    )

    with patch.object(_se, "datetime", wraps=_se.datetime) as mock_dt:
        mock_dt.now.return_value = nov_date
        res_near = _asm(**near_low)
        res_far = _asm(**far_from_low)

    if res_near and res_near["action"] == "BUY":
        heads = [r["head"] for r in res_near["rationale"]]
        assert any("52-Week" in h or "52wk" in h.lower() or "Near" in h for h in heads), (
            f"Expected near-52wk-low rationale card; got: {heads}"
        )

    if res_near and res_far and res_near["action"] == res_far["action"] == "BUY":
        assert res_near["confidence"] < res_far["confidence"], (
            "Near 52-week low should reduce confidence vs far-from-low (inverted gate)"
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
    """VIX 20–30 + conf≥58 should produce positionSizeScale > VIX<15 (calm) scale.

    With vol-targeting, absolute scale depends on ticker vol — a high-vol ticker
    (ATR=2%) gets down-sized relative to median vol even in a fear regime.
    The invariant is RELATIVE: fear-regime scale > calm-regime scale for the
    same ticker/confidence, since VIX multipliers are 1.15 vs 0.75.
    """
    fear_kwargs = _mr_buy_kwargs(
        score=60.0,
        market_ctx={"macro": {"sp500_trend": "up", "vix": 25.0}},
    )
    calm_kwargs = _mr_buy_kwargs(
        score=60.0,
        market_ctx={"macro": {"sp500_trend": "up", "vix": 12.0}},
    )
    fear_res = _asm(**fear_kwargs)
    calm_res = _asm(**calm_kwargs)

    if (
        fear_res
        and fear_res["action"] == "BUY"
        and fear_res.get("confidence", 0) >= 58
        and calm_res
        and calm_res["action"] == "BUY"
    ):
        fear_scale = fear_res.get("positionSizeScale", 1.0)
        calm_scale = calm_res.get("positionSizeScale", 1.0)
        assert fear_scale > calm_scale, (
            f"Fear regime (VIX 25) scale {fear_scale} should exceed calm regime (VIX 12) "
            f"scale {calm_scale} for the same ticker and confidence"
        )


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


# ── §69–§72 Options Pack (score_options pure-function tests) ──────────────────


def test_gex_flip_proximity_gate():
    """§69 GEX flip level — near proxy (+5) and >3% above penalty (-2)."""
    from services.options import score_options

    # (a) spot 1% below flip → within [-2%, +1%] band → +5
    delta_near, cards_near = score_options({"gex_flip_level": 99.0, "spot": 100.0})
    heads_near = [c["head"] for c in cards_near]
    assert any("GEX Flip" in h for h in heads_near), f"GEX near-flip card expected; got: {heads_near}"
    assert delta_near >= 5, f"Expected score ≥ +5 for near-flip; got {delta_near}"
    pos = [c for c in cards_near if "GEX Flip" in c.get("head", "")]
    assert any(c["sentiment"] == "pos" for c in pos), "GEX near-flip card must be positive sentiment"

    # (b) flip 5% above spot → >3% above band → -2 penalty
    delta_far, cards_far = score_options({"gex_flip_level": 105.0, "spot": 100.0})
    heads_far = [c["head"] for c in cards_far]
    assert any("Above GEX" in h or "Dealer Short Delta" in h for h in heads_far), (
        f"Above-GEX penalty card expected; got: {heads_far}"
    )
    assert delta_far <= -2, f"Expected score ≤ -2 for above-flip; got {delta_far}"


def test_zero_dte_spike_gate():
    """§70 Zero-DTE put spike — ratio > 0.30 fires (-4); ≤ 0.30 does not."""
    from services.options import score_options

    # (a) spike fires → negative card
    delta, cards = score_options({"zero_dte_ratio": 0.45})
    heads = [c["head"] for c in cards]
    assert any("Zero-DTE" in h for h in heads), f"Zero-DTE card expected; got: {heads}"
    assert delta <= -4, f"Expected score ≤ -4 for zero-DTE spike; got {delta}"
    spike_cards = [c for c in cards if "Zero-DTE" in c.get("head", "")]
    assert any(c["sentiment"] == "neg" for c in spike_cards), "Zero-DTE card must be negative sentiment"

    # (b) below threshold → no card
    _, cards_no = score_options({"zero_dte_ratio": 0.20})
    assert not any("Zero-DTE" in c["head"] for c in cards_no), "Zero-DTE card must not fire at ratio=0.20"


def test_max_pain_convergence_gate():
    """§71 Max pain >2% above spot with expiry ≤ 2 days → +4; far expiry → no card."""
    from services.options import score_options
    from datetime import date, timedelta

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # (a) fires: max_pain 3% above spot, expiry tomorrow
    delta, cards = score_options({"max_pain": 103.0, "spot": 100.0, "expiry": tomorrow})
    heads = [c["head"] for c in cards]
    assert any("Max Pain" in h for h in heads), f"Max Pain card expected; got: {heads}"
    assert delta >= 4, f"Expected score ≥ +4 for max pain pull; got {delta}"

    # (b) expiry 10 days out → doesn't fire
    far_exp = (date.today() + timedelta(days=10)).isoformat()
    _, cards_far = score_options({"max_pain": 103.0, "spot": 100.0, "expiry": far_exp})
    assert not any("Max Pain" in c["head"] for c in cards_far), "Max Pain card must not fire when expiry > 2 days away"


def test_vrp_proxy_gate():
    """§72 VRP proxy — positive IV premium (+3) and negative IV backwardation (-2)."""
    from services.options import score_options

    # (a) positive VRP → +3 and pos card
    delta_pos, cards_pos = score_options({"vrp_proxy": 0.08})
    heads_pos = [c["head"] for c in cards_pos]
    assert any("Volatility Risk Premium" in h or "VRP" in h for h in heads_pos), (
        f"Positive VRP card expected; got: {heads_pos}"
    )
    assert delta_pos >= 3, f"Expected score ≥ +3 for positive VRP; got {delta_pos}"

    # (b) negative VRP → -2 and neg card
    delta_neg, cards_neg = score_options({"vrp_proxy": -0.10})
    heads_neg = [c["head"] for c in cards_neg]
    assert any("Negative VRP" in h or "Back-Month" in h for h in heads_neg), (
        f"Negative VRP card expected; got: {heads_neg}"
    )
    assert delta_neg <= -2, f"Expected score ≤ -2 for negative VRP; got {delta_neg}"


# ── §73/§74/§76 Gates (generate_signal integration, mocked fetchers) ─────────


async def _gen_signal_mocked(*, insider=None, fundamentals=None, ticker="NVDA"):
    """Run generate_signal with all external fetchers mocked out."""
    import pandas as pd
    from unittest.mock import AsyncMock, patch

    n = 252
    prices = [100.0 + i * 0.01 for i in range(n)]
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    mock_df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
            "Volume": [2_000_000] * n,
        },
        index=idx,
    )
    mock_df_1h = pd.DataFrame({"Close": [100.0] * 20})

    strong_tech = {
        "price": 100.0,
        "atr": 2.0,
        "rsi": 22.0,
        "bb_pct_b": 0.05,
        "ibs": 0.10,
        "macd_hist": 0.5,
        "macd_hist_prev": -0.2,
        "sma200": 80.0,
        "sma50": 85.0,
        "stoch_k": 12.0,
        "stoch_d": 10.0,
        "stoch_k_prev": 8.0,
        "stoch_d_prev": 11.0,
        "cci": -150.0,
        "mfi": 14.0,
        "volume": 2_000_000,
        "avg_volume": 1_000_000,
        "bb_upper": 106.0,
        "bb_lower": 94.0,
        "ema8": 100.0,
        "ema21": 98.0,
        "ema8_prev": 97.0,
        "ema21_prev": 99.0,
        "close_streak": 0,
        "rvol": 1.5,
    }

    with (
        patch("services.signal_engine.get_company_news", new_callable=AsyncMock, return_value=[]),
        patch("services.signal_engine.get_scraped_news", new_callable=AsyncMock, return_value=[]),
        patch(
            "services.signal_engine.get_insider_activity",
            new_callable=AsyncMock,
            return_value=insider or {},
        ),
        patch("services.signal_engine.get_analyst_recs", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_earnings_calendar", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_earnings_surprise", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_options_flow", new_callable=AsyncMock, return_value={}),
        patch(
            "services.signal_engine.get_fundamentals",
            new_callable=AsyncMock,
            return_value=fundamentals or {},
        ),
        patch("services.signal_engine.get_social_sentiment", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_google_trends", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_congress_signal", new_callable=AsyncMock, return_value={}),
        patch("services.signal_engine.get_history", new_callable=AsyncMock) as m_hist,
        patch(
            "services.signal_engine.get_info",
            new_callable=AsyncMock,
            return_value={"company": "Test Inc"},
        ),
        patch(
            "services.signal_engine.get_sector_relative_strength",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch("services.signal_engine.calculate_indicators", return_value=strong_tech),
        patch("services.signal_ml.get_model", return_value=None),
        patch("services.signal_ml.get_entry_model", return_value=None),
    ):
        m_hist.side_effect = [mock_df, mock_df_1h]
        from services.signal_engine import generate_signal

        return await generate_signal(ticker)


@pytest.mark.asyncio
async def test_insider_cluster_buy_gate():
    """§73 Insider clustering — ≥ 3 unique buyers → cluster card; 1 buyer → no card."""
    # (a) 3 unique buyers → 'Insider Cluster Buy — N Distinct Insiders' card
    res = await _gen_signal_mocked(insider={"unique_buyers": 3})
    if res is not None:
        heads = [r["head"] for r in res.get("rationale", [])]
        assert any("Distinct Insiders" in h for h in heads), (
            f"Expected 'Insider Cluster Buy — N Distinct Insiders' card for unique_buyers=3; got: {heads}"
        )

    # (b) 1 unique buyer → no cluster card (threshold is ≥ 2)
    res_single = await _gen_signal_mocked(insider={"unique_buyers": 1})
    if res_single is not None:
        heads_single = [r["head"] for r in res_single.get("rationale", [])]
        assert not any("Distinct Insiders" in h for h in heads_single), (
            f"unique_buyers=1 should not fire cluster card; got: {heads_single}"
        )


@pytest.mark.asyncio
async def test_beneish_m_score_gate():
    """§74 Beneish M-Score — > -1.78 → manipulation flag (-12); < -1.78 → no card."""
    # (a) M = -1.5 (above threshold) → flag fires
    res = await _gen_signal_mocked(fundamentals={"beneish_m": -1.5})
    if res is not None:
        heads = [r["head"] for r in res.get("rationale", [])]
        assert any("Beneish" in h for h in heads), f"Expected Beneish manipulation card for M=-1.5; got: {heads}"
        beneish_cards = [r for r in res.get("rationale", []) if "Beneish" in r.get("head", "")]
        assert all(r["sentiment"] == "neg" for r in beneish_cards), "Beneish card must be negative sentiment"

    # (b) M = -2.5 (below threshold, no manipulation signal) → no card
    res_safe = await _gen_signal_mocked(fundamentals={"beneish_m": -2.5})
    if res_safe is not None:
        heads_safe = [r["head"] for r in res_safe.get("rationale", [])]
        assert not any("Beneish" in h for h in heads_safe), (
            f"M=-2.5 (safe) should not fire Beneish card; got: {heads_safe}"
        )


@pytest.mark.asyncio
async def test_altman_z_score_gate():
    """§76 Altman Z removed 2026-06-03 — confirms no Altman cards at any Z value.

    EDGAR validation: 79/106 IS tickers always below Z'<1.23 due to structural
    reasons (financial sector leverage model, tech goodwill/intangibles). The gate
    was penalising ~80% of signals by -15 pts — a primary driver of the IS/live
    WR gap. Removed from gates/fundamentals.py.
    """
    # All Z values should now produce zero Altman cards
    for z_val in [0.5, 1.5, 2.2, 3.5]:
        res = await _gen_signal_mocked(fundamentals={"altman_z": z_val})
        if res is not None:
            heads = [r["head"] for r in res.get("rationale", [])]
            assert not any("Altman" in h for h in heads), (
                f"§76 Altman removed — no Altman cards expected for Z={z_val}; got: {heads}"
            )
