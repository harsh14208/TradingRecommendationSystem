"""Coverage tests for small uncovered modules."""

from datetime import datetime
from unittest.mock import patch

import pandas as pd


# ── schemas.py ─────────────────────────────────────────────────────────────


def test_api_response_defaults():
    from schemas import ApiResponse

    r = ApiResponse(data={"foo": "bar"})
    assert r.ok is True
    assert r.error is None
    assert r.meta is None
    dumped = r.model_dump()
    assert "ok" in dumped
    assert "data" in dumped
    assert "error" not in dumped  # excluded because None
    assert "meta" not in dumped


def test_api_response_error():
    from schemas import ApiResponse

    r = ApiResponse(ok=False, error="boom")
    dumped = r.model_dump()
    assert dumped["ok"] is False
    assert dumped["error"] == "boom"
    assert "data" not in dumped


def test_api_response_with_meta():
    from schemas import ApiResponse

    r = ApiResponse(data=[], meta={"total": 5})
    dumped = r.model_dump()
    assert dumped["meta"] == {"total": 5}


# ── services/cohort_service.py ─────────────────────────────────────────────


def test_allocate_signal_cohort_buckets():
    from services.cohort_service import allocate_signal_cohort

    ts = datetime(2026, 1, 15, 10, 0, 0)
    # Deterministic: same ticker+ts always yields same cohort
    c1 = allocate_signal_cohort("AAPL", ts)
    c2 = allocate_signal_cohort("AAPL", ts)
    assert c1 == c2
    assert c1 in {"delivered", "shadow", "withheld"}


def test_build_policy_version_meta():
    from services.cohort_service import (
        build_policy_version_meta,
        SCORING_POLICY_VERSION,
        GATES_POLICY_VERSION,
        ML_MODEL_ID,
    )

    ts = datetime(2026, 1, 15, 10, 0, 0)
    meta = build_policy_version_meta("AAPL", ts, meta_prob=0.75)
    assert meta["cohort"] in {"delivered", "shadow", "withheld"}
    assert meta["policy_versions"]["scoring"] == SCORING_POLICY_VERSION
    assert meta["policy_versions"]["gates"] == GATES_POLICY_VERSION
    assert meta["policy_versions"]["ml_model"] == ML_MODEL_ID
    assert meta["meta_label_probability"] == 0.75
    assert "allocated_at" in meta


# ── services/gates/statistical.py ──────────────────────────────────────────


def test_apply_statistical_gates_no_data():
    from services.gates.statistical import apply_statistical_gates

    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=pd.DataFrame(),
        is_lev_etf=False,
    )
    assert score == 10.0
    assert cards == []
    assert sources == set()


def test_apply_statistical_gates_lev_etf_skipped():
    from services.gates.statistical import apply_statistical_gates

    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": pd.Series([1, 2, 3])}},
        df=pd.DataFrame({"Close": range(100)}),
        is_lev_etf=True,
    )
    assert score == 10.0
    assert cards == []


@patch("services.technicals.compute_cointegration_zscore")
def test_apply_statistical_gates_cointegration_below_minus2(mock_zscore):
    from services.gates.statistical import apply_statistical_gates

    mock_zscore.return_value = -2.5
    df = pd.DataFrame({"Close": range(100)})
    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": pd.Series(range(100))}},
        df=df,
        is_lev_etf=False,
    )
    assert score == 14.0
    assert len(cards) == 1
    assert "Cointegration Deviation" in cards[0]["head"]
    assert "Technical" in sources


@patch("services.technicals.compute_cointegration_zscore")
def test_apply_statistical_gates_cointegration_between_minus2_and_minus1(mock_zscore):
    from services.gates.statistical import apply_statistical_gates

    mock_zscore.return_value = -1.5
    df = pd.DataFrame({"Close": range(100)})
    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": pd.Series(range(100))}},
        df=df,
        is_lev_etf=False,
    )
    assert score == 12.0
    assert len(cards) == 1
    assert "Sector Pair Deviation" in cards[0]["head"]


@patch("services.technicals.compute_cointegration_zscore")
def test_apply_statistical_gates_cointegration_above_half(mock_zscore):
    from services.gates.statistical import apply_statistical_gates

    mock_zscore.return_value = 1.0
    df = pd.DataFrame({"Close": range(100)})
    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": pd.Series(range(100))}},
        df=df,
        is_lev_etf=False,
    )
    assert score == 8.0
    assert len(cards) == 1
    assert "Above Sector Pair Mean" in cards[0]["head"]


@patch("services.technicals.compute_cointegration_zscore", side_effect=Exception("boom"))
def test_apply_statistical_gates_exception_graceful(mock_zscore):
    from services.gates.statistical import apply_statistical_gates

    df = pd.DataFrame({"Close": range(100)})
    score, cards, sources = apply_statistical_gates(
        score=10.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": pd.Series(range(100))}},
        df=df,
        is_lev_etf=False,
    )
    assert score == 10.0
    assert cards == []
    assert sources == set()


# ── services/engines/scorers.py ────────────────────────────────────────────


def test_score_moving_averages_block():
    from services.engines.scorers import score_moving_averages_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 105.0
    ctx.tech = {"sma50": 100.0, "sma200": 95.0}
    ctx._is_low_atr = False

    with patch("services.signal_scoring.score_moving_averages") as mock_ma:
        mock_ma.return_value = (8.0, [{"src": "Technical", "head": "MA cross", "sentiment": "pos"}])
        score_moving_averages_block(ctx)
        assert ctx.ma_score == 8.0
        assert any("MA cross" in r["head"] for r in ctx.rationale)
        assert ctx.score == 8.0


def test_score_moving_averages_block_low_atr():
    from services.engines.scorers import score_moving_averages_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 105.0
    ctx.tech = {"sma50": 100.0, "sma200": 95.0}
    ctx._is_low_atr = True

    with patch("services.signal_scoring.score_moving_averages") as mock_ma:
        mock_ma.return_value = (8.0, [])
        score_moving_averages_block(ctx)
        assert ctx.ma_score == 8.0
        assert ctx.score == 0.0  # not added when low atr


def test_score_bollinger_bands_block_deep_oversold():
    from services.engines.scorers import score_bollinger_bands_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 100.0
    ctx.tech = {"bb_pct_b": 0.03, "rsi": 30}
    score_bollinger_bands_block(ctx)
    assert ctx.mean_rev_score == 18.0
    assert any("BB Extreme Oversold" in r["head"] for r in ctx.rationale)


def test_score_bollinger_bands_block_near_lower_band():
    from services.engines.scorers import score_bollinger_bands_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 100.0
    ctx.tech = {"bb_pct_b": 0.10, "rsi": 40}
    score_bollinger_bands_block(ctx)
    assert ctx.mean_rev_score == 5.0
    assert any("BB Near Lower Band" in r["head"] for r in ctx.rationale)


def test_score_bollinger_bands_block_extreme_overbought():
    from services.engines.scorers import score_bollinger_bands_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 100.0
    ctx.tech = {"bb_pct_b": 0.97, "rsi": 70}
    score_bollinger_bands_block(ctx)
    assert ctx.mean_rev_score == -14.0
    assert any("BB Extreme Overbought" in r["head"] for r in ctx.rationale)


def test_score_bollinger_bands_block_band_touch():
    from services.engines.scorers import score_bollinger_bands_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 94.5
    ctx.tech = {"bb_lower": 94.5, "bb_upper": 105.0}
    score_bollinger_bands_block(ctx)
    assert ctx.mean_rev_score == 6.0
    assert any("Lower Bollinger Band Touch" in r["head"] for r in ctx.rationale)


def test_score_bollinger_bands_block_no_bb_data():
    from services.engines.scorers import score_bollinger_bands_block
    from services.engines.context import ScoringContext

    df = pd.DataFrame({"Close": [100.0] * 10})
    ctx = ScoringContext(ticker="AAPL", df=df, info={})
    ctx.price = 100.0
    ctx.tech = {}
    score_bollinger_bands_block(ctx)
    assert ctx.mean_rev_score == 0.0
    assert not any("BB" in r.get("head", "") for r in ctx.rationale)
