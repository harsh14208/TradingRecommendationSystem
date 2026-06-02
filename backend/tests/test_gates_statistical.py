"""
Unit tests for gates/statistical.py — apply_statistical_gates().

Covers §59 OU halflife, §60 Hurst, §61 idio vol, §63 sector cointegration.
All tests are pure-function calls (no DB, no network, no async).
"""

import pandas as pd
import numpy as np
import pytest

from services.gates.statistical import apply_statistical_gates


def _df(n: int = 100, vol: float = 0.030) -> pd.DataFrame:
    """Minimal OHLCV DataFrame with a Close column.
    Default vol=0.030 → ~35.4% annualised (seed 42) — in the neutral idio-vol
    range (25–55%) so the §61 gate doesn't fire and confound other gate tests.
    """
    rng = np.random.default_rng(42)
    closes = 100.0 * np.cumprod(1 + rng.normal(0, vol, n))
    return pd.DataFrame({"Close": closes})


# ── §60 Hurst ────────────────────────────────────────────────────────────────


def test_hurst_trending_positive_score():
    """Hurst > 0.60 + positive score → trend bonus +5."""
    score, cards, _ = apply_statistical_gates(
        score=20.0,
        tech={"hurst": 0.70},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(25.0)
    assert any("Hurst" in c["head"] for c in cards)


def test_hurst_trending_negative_score():
    """Hurst > 0.60 + negative score → trend bonus −5."""
    score, _, _ = apply_statistical_gates(
        score=-20.0,
        tech={"hurst": 0.70},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(-25.0)


def test_hurst_trending_zero_score():
    """Hurst > 0.60 + zero score → no bonus."""
    score, _, _ = apply_statistical_gates(
        score=0.0,
        tech={"hurst": 0.70},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(0.0)


def test_hurst_mr_regime_large_score_damped():
    """Hurst < 0.40 + |score| > 15 → score *= 0.87."""
    score, cards, _ = apply_statistical_gates(
        score=20.0,
        tech={"hurst": 0.35},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(20.0 * 0.87)
    assert any("Mean-Reverting" in c["head"] for c in cards)


def test_hurst_mr_regime_small_score_unchanged():
    """Hurst < 0.40 + |score| ≤ 15 → score unchanged (only rationale added)."""
    score, _, _ = apply_statistical_gates(
        score=10.0,
        tech={"hurst": 0.35},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(10.0)


def test_hurst_neutral_range_no_change():
    """Hurst 0.40–0.60 → no score change, no cards."""
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={"hurst": 0.50},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)
    assert not any("Hurst" in c.get("head", "") for c in cards)


# ── §59 OU halflife ──────────────────────────────────────────────────────────


def test_ou_slow_reversion_penalised():
    """ou_halflife > 12 → −5."""
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={"ou_halflife": 15.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(25.0)
    assert any("Slow OU" in c["head"] for c in cards)


def test_ou_fast_reversion_boosted():
    """ou_halflife < 5 → +4."""
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={"ou_halflife": 3.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(34.0)
    assert any("Fast OU" in c["head"] for c in cards)


def test_ou_middle_range_no_change():
    """ou_halflife 5–12 → no score change."""
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={"ou_halflife": 8.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)


def test_ou_skipped_for_lev_etf():
    """ou_halflife gate skipped for leveraged ETFs."""
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={"ou_halflife": 15.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=True,
    )
    assert score == pytest.approx(30.0)


# ── §61 Idiosyncratic Volatility ─────────────────────────────────────────────


def test_high_idiovol_penalised():
    """High idiosyncratic vol (>55%) → −5."""
    df = _df(n=100, vol=0.035)  # ~55%+ annualised
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=df,
        is_lev_etf=False,
    )
    # only check if triggered (depends on random seed / actual vol)
    ivol = float(df["Close"].pct_change().dropna().values[-63:].std(ddof=1)) * np.sqrt(252) * 100
    if ivol > 55.0:
        assert score == pytest.approx(25.0)
        assert any("Idiosyncratic" in c["head"] for c in cards)


def test_low_idiovol_boosted():
    """Low idiosyncratic vol (<25%) → +2."""
    df = _df(n=100, vol=0.005)  # ~8% annualised — well below 25%
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=df,
        is_lev_etf=False,
    )
    ivol = float(df["Close"].pct_change().dropna().values[-63:].std(ddof=1)) * np.sqrt(252) * 100
    if ivol < 25.0:
        assert score == pytest.approx(32.0)
        assert any("Stable Reverter" in c["head"] for c in cards)


def test_idiovol_skipped_short_df():
    """DataFrame shorter than 63 bars → vol gate skipped."""
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=_df(n=50),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)


def test_idiovol_skipped_lev_etf():
    """Leveraged ETF → vol gate skipped."""
    df = _df(n=100, vol=0.035)
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=df,
        is_lev_etf=True,
    )
    assert score == pytest.approx(30.0)


# ── §63 Sector cointegration ─────────────────────────────────────────────────


def test_no_sector_rs_no_cointegration():
    """Missing sector_rs → cointegration gate skipped, no crash."""
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)
    assert not any("Cointegration" in c.get("head", "") for c in cards)


def test_missing_etf_in_context_no_crash():
    """sector_etf present but not in etf_histories → skipped gracefully."""
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {}},
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)


# ── Combined / no-op ─────────────────────────────────────────────────────────


def test_empty_tech_dict_no_crash():
    """Empty tech dict → all gates no-op, returns original score."""
    score, cards, sources = apply_statistical_gates(
        score=55.0,
        tech={},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert isinstance(cards, list)
    assert isinstance(sources, set)


def test_returns_correct_types():
    """Return type is (float, list, set)."""
    result = apply_statistical_gates(
        score=30.0,
        tech={"hurst": 0.5, "ou_halflife": 8.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert isinstance(result[0], float)
    assert isinstance(result[1], list)
    assert isinstance(result[2], set)
