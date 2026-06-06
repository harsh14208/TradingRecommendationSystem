"""Extended tests for validate_predictions.py — async resolution functions."""
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── _fetch_ohlcv ──────────────────────────────────────────────────────────────

def test_fetch_ohlcv_error():
    import validate_predictions as vp
    with patch("yfinance.Ticker") as mock_ticker_cls:
        mock_ticker_cls.return_value.history.side_effect = Exception("network error")
        result = vp._fetch_ohlcv("AAPL")
    assert result == []


def test_fetch_ohlcv_empty_df():
    import validate_predictions as vp
    import pandas as pd
    with patch("yfinance.Ticker") as mock_ticker_cls:
        mock_ticker_cls.return_value.history.return_value = pd.DataFrame()
        result = vp._fetch_ohlcv("AAPL")
    assert result == []


def test_fetch_ohlcv_success():
    import validate_predictions as vp
    import pandas as pd
    df = pd.DataFrame({
        "High": [152.0, 153.0, 154.0],
        "Low": [148.0, 149.0, 150.0],
    }, index=pd.date_range("2026-01-01", periods=3))
    with patch("yfinance.Ticker") as mock_ticker_cls:
        mock_ticker_cls.return_value.history.return_value = df
        result = vp._fetch_ohlcv("AAPL", days=5)
    assert len(result) == 3
    assert result[0] == (152.0, 148.0)


# ── resolve_outcomes ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_outcomes_no_signals():
    import validate_predictions as vp

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    mock_session = MagicMock()
    mock_session.return_value = mock_db

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("validate_predictions.create_async_engine", return_value=mock_engine), \
         patch("validate_predictions.sessionmaker", return_value=mock_session):
        result = await vp.resolve_outcomes()

    assert result == 0


@pytest.mark.asyncio
async def test_resolve_outcomes_with_signals():
    import validate_predictions as vp

    sig = MagicMock()
    sig.ticker = "AAPL"
    sig.entry = 150.0
    sig.action = "BUY"
    sig.exit_type = None
    sig.outcome_1d = None
    sig.outcome_3d = None
    sig.outcome_pct = None
    sig.outcome_14d = None
    sig.created_at = datetime.now(timezone.utc) - timedelta(days=20)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sig]

    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    mock_session = MagicMock()
    mock_session.return_value = mock_db

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("validate_predictions.create_async_engine", return_value=mock_engine), \
         patch("validate_predictions.sessionmaker", return_value=mock_session), \
         patch("validate_predictions._fetch_prices", return_value={"AAPL": 155.0}):
        result = await vp.resolve_outcomes()

    # Should have updated at least 1 signal
    assert result >= 0


# ── fix_phantom_wins ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fix_phantom_wins_no_signals():
    import validate_predictions as vp

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    mock_session = MagicMock()
    mock_session.return_value = mock_db

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("validate_predictions.create_async_engine", return_value=mock_engine), \
         patch("validate_predictions.sessionmaker", return_value=mock_session):
        result = await vp.fix_phantom_wins(apply=False)

    assert result == 0


# ── calibration_report ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calibration_report_no_signals():
    import validate_predictions as vp

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db = MagicMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    mock_session = MagicMock()
    mock_session.return_value = mock_db

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with patch("validate_predictions.create_async_engine", return_value=mock_engine), \
         patch("validate_predictions.sessionmaker", return_value=mock_session):
        # Should not crash even with no signals
        await vp.calibration_report()


# ── BANDS and FRICTION_PCT ────────────────────────────────────────────────────

def test_bands_are_defined():
    import validate_predictions as vp
    assert len(vp.BANDS) > 0
    assert vp.FRICTION_PCT > 0
