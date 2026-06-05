"""
Unit tests for gates/statistical.py — apply_statistical_gates().

Covers §63 sector cointegration only.
§59/§60/§61 removed 2026-06-02: all confirmed dead gates
(--validate-live-gates: ΔSh=0.00, ΔN ≤ 8 each).
All tests are pure-function calls (no DB, no network, no async).
"""

import pandas as pd
import numpy as np
import pytest

from services.gates.statistical import apply_statistical_gates


def _df(n: int = 100, vol: float = 0.030) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    closes = 100.0 * np.cumprod(1 + rng.normal(0, vol, n))
    return pd.DataFrame({"Close": closes})


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
    assert score == pytest.approx(55.0)
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


def test_lev_etf_no_cointegration():
    """Leveraged ETF → cointegration gate skipped."""
    score, cards, _ = apply_statistical_gates(
        score=30.0,
        tech={},
        sector_rs={"sector_etf": "XLK"},
        market_ctx={"etf_histories": {"XLK": _df()}},
        df=_df(),
        is_lev_etf=True,
    )
    assert score == pytest.approx(30.0)
    assert not any("Cointegration" in c.get("head", "") for c in cards)


def test_removed_gates_no_longer_affect_score():
    """§59/§60/§61 data in tech dict → score unchanged (gates removed)."""
    score, _, _ = apply_statistical_gates(
        score=30.0,
        tech={"hurst": 0.70, "ou_halflife": 15.0},
        sector_rs=None,
        market_ctx=None,
        df=_df(),
        is_lev_etf=False,
    )
    assert score == pytest.approx(30.0)
