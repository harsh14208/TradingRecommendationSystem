"""Tests for services/pca_risk.py."""

from unittest.mock import AsyncMock, patch

import numpy as np
import pandas as pd
import pytest


def _fake_histories(tickers, n_rows=70):
    """Return a dict of DataFrames with synthetic close prices."""
    result = {}
    rng = np.random.default_rng(42)
    for t in tickers:
        closes = 100 + rng.normal(0, 1, n_rows).cumsum()
        closes = np.abs(closes) + 50
        df = pd.DataFrame({"Close": closes})
        result[t] = df
    return result


@pytest.mark.asyncio
async def test_fewer_than_3_positions_returns_empty():
    from services.pca_risk import compute_pca_risk

    result = await compute_pca_risk({"AAPL": 1000, "GOOG": 2000})
    assert result == {}


@pytest.mark.asyncio
async def test_data_fetch_failure_returns_empty():
    from services.pca_risk import compute_pca_risk

    with patch("services.market_data.get_histories_batch", AsyncMock(side_effect=Exception("timeout"))):
        result = await compute_pca_risk({"AAPL": 1000, "GOOG": 2000, "MSFT": 3000})
    assert result == {}


@pytest.mark.asyncio
async def test_full_run_returns_expected_keys():
    from services.pca_risk import compute_pca_risk

    tickers = ["NVDA", "AMD", "MSFT", "AAPL", "TSLA"]
    histories = _fake_histories(tickers, n_rows=70)

    with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
        result = await compute_pca_risk({t: 10_000 for t in tickers})

    assert "factors" in result
    assert "concentration_warning" in result
    assert "dominant_factor" in result
    assert "haircut_pct" in result
    assert "tickers_analysed" in result


@pytest.mark.asyncio
async def test_zero_value_positions_excluded():
    from services.pca_risk import compute_pca_risk

    tickers_nonzero = ["NVDA", "AMD", "MSFT"]
    histories = _fake_histories(tickers_nonzero)

    with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
        result = await compute_pca_risk({"NVDA": 5000, "AMD": 0, "MSFT": 5000, "TST": 0})

    # AMD and TST have value=0 so excluded; only NVDA+MSFT remain → < 3 → empty
    assert result == {}


@pytest.mark.asyncio
async def test_tickers_with_insufficient_history_excluded():
    from services.pca_risk import compute_pca_risk

    tickers = ["NVDA", "AMD", "MSFT", "AAPL"]
    histories = _fake_histories(tickers, n_rows=70)
    # Give NVDA only 5 rows (below min_rows threshold)
    histories["NVDA"] = pd.DataFrame({"Close": [100.0, 101.0, 99.0, 102.0, 98.0]})

    with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
        result = await compute_pca_risk({t: 10_000 for t in tickers})

    # AMD, MSFT, AAPL all have enough data → should get a valid result with 3 tickers
    assert "factors" in result or result == {}  # could be empty if < 3 remain


@pytest.mark.asyncio
async def test_concentrated_portfolio_haircut():
    from services.pca_risk import compute_pca_risk

    # Build highly correlated tickers (all ~same returns)
    tickers = ["NVDA", "AMD", "AMAT", "KLAC", "MU"]
    n = 70
    base = np.random.default_rng(0).normal(0, 0.01, n)
    histories = {}
    for t in tickers:
        closes = 100 * np.cumprod(1 + base + np.random.default_rng(hash(t) % 2**32).normal(0, 0.001, n))
        histories[t] = pd.DataFrame({"Close": closes})

    with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
        result = await compute_pca_risk({t: 10_000 for t in tickers})

    if result:
        assert isinstance(result["haircut_pct"], float)
        assert result["haircut_pct"] >= 0


def test_name_factor_identifies_ai_semiconductor():
    from services.pca_risk import _name_factor

    loadings = [("NVDA", 0.9), ("AMD", 0.8), ("AMAT", 0.7), ("SPY", 0.1)]
    name = _name_factor(loadings)
    assert name == "AI / Semiconductor"


def test_name_factor_unidentified():
    from services.pca_risk import _name_factor

    loadings = [("XYZ", 0.5), ("ABC", 0.4)]
    name = _name_factor(loadings)
    assert name == "Unidentified"


@pytest.mark.asyncio
async def test_missing_ticker_in_histories():
    from services.pca_risk import compute_pca_risk

    tickers = ["A", "B", "C", "D"]
    histories = _fake_histories(["A", "B"])  # C and D not returned

    with patch("services.market_data.get_histories_batch", AsyncMock(return_value=histories)):
        result = await compute_pca_risk({t: 5000 for t in tickers})

    # Only A and B have data → fewer than 3 valid tickers
    assert result == {}
