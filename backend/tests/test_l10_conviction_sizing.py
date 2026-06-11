"""§87 L10 conviction-tier sizing — scanner-level unit tests.

Backtest-validated 2026-06-10 (v10.9 canon): prev-day BUY → 1.3× size,
Sharpe 0.24→0.30 weighted, ΔN=0. These tests cover the live proxy logic
(prior-trading-day BUY lookup), the multiplier, and the global stack clamp.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services import scanner as scanner_mod
from services.scanner import _SIZE_SCALE_CLAMP, _apply_l10_conviction_sizing


def _mock_session(rows):
    """Async-context-manager session whose execute() returns the given rows."""
    result = MagicMock()
    result.all.return_value = rows
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


def _row(ticker: str, created_at: datetime):
    row = MagicMock()
    row.ticker = ticker
    row.created_at = created_at
    return row


@pytest.mark.asyncio
async def test_prev_day_buy_gets_boost_and_rationale():
    yesterday = datetime.utcnow() - timedelta(days=1)
    signals = [{"ticker": "NVDA", "action": "BUY", "positionSizeScale": 1.0, "rationale": []}]
    with patch.object(scanner_mod, "AsyncSessionLocal", return_value=_mock_session([_row("NVDA", yesterday)])):
        await _apply_l10_conviction_sizing(signals)
    assert signals[0]["positionSizeScale"] == 1.3
    assert any("§87" in c.get("head", "") for c in signals[0]["rationale"])


@pytest.mark.asyncio
async def test_no_prev_day_buy_no_boost():
    signals = [{"ticker": "NVDA", "action": "BUY", "positionSizeScale": 1.0, "rationale": []}]
    with patch.object(scanner_mod, "AsyncSessionLocal", return_value=_mock_session([])):
        await _apply_l10_conviction_sizing(signals)
    assert signals[0]["positionSizeScale"] == 1.0
    assert signals[0]["rationale"] == []


@pytest.mark.asyncio
async def test_only_latest_prior_day_counts():
    # BUY three days ago but NOT on the most recent prior signal day → no boost
    # (semantic = consecutive scan days, mirroring backtest consecutive bars).
    old = datetime.utcnow() - timedelta(days=3)
    recent = datetime.utcnow() - timedelta(days=1)
    rows = [_row("NVDA", old), _row("AMD", recent)]
    signals = [
        {"ticker": "NVDA", "action": "BUY", "positionSizeScale": 1.0, "rationale": []},
        {"ticker": "AMD", "action": "BUY", "positionSizeScale": 1.0, "rationale": []},
    ]
    with patch.object(scanner_mod, "AsyncSessionLocal", return_value=_mock_session(rows)):
        await _apply_l10_conviction_sizing(signals)
    assert signals[0]["positionSizeScale"] == 1.0  # NVDA: stale prior day
    assert signals[1]["positionSizeScale"] == 1.3  # AMD: consecutive day


@pytest.mark.asyncio
async def test_global_clamp_caps_stack():
    yesterday = datetime.utcnow() - timedelta(days=1)
    signals = [
        {"ticker": "NVDA", "action": "BUY", "positionSizeScale": 2.8, "rationale": []},  # 2.8×1.3=3.64 → 3.0
        {"ticker": "MSFT", "action": "HOLD", "positionSizeScale": 5.0, "rationale": []},  # clamp applies to all
    ]
    with patch.object(scanner_mod, "AsyncSessionLocal", return_value=_mock_session([_row("NVDA", yesterday)])):
        await _apply_l10_conviction_sizing(signals)
    assert signals[0]["positionSizeScale"] == _SIZE_SCALE_CLAMP[1]
    assert signals[1]["positionSizeScale"] == _SIZE_SCALE_CLAMP[1]


@pytest.mark.asyncio
async def test_missing_or_invalid_scale_untouched():
    signals = [
        {"ticker": "NVDA", "action": "BUY", "rationale": []},  # no scale key
        {"ticker": "AMD", "action": "BUY", "positionSizeScale": 0, "rationale": []},
    ]
    with patch.object(scanner_mod, "AsyncSessionLocal", return_value=_mock_session([])):
        await _apply_l10_conviction_sizing(signals)
    assert "positionSizeScale" not in signals[0]
    assert signals[1]["positionSizeScale"] == 0
