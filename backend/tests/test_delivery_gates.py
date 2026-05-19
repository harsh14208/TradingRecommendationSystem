"""
Tests for services/delivery_gates.py.

Each gate is tested in isolation via a minimal sig_dict and a mock DB + settings.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sig(**kwargs):
    base = {
        "ticker": "AAPL", "action": "BUY", "confidence": 65.0,
        "style": "position", "sectorEtf": "XLK",
        "sources": ["Options", "13F"], "entry": 100.0, "target": 110.0,
        "daysToEarnings": 30,
    }
    base.update(kwargs)
    return base


class _Settings:
    min_confidence = 55.0


async def _db_no_sector_count():
    """Mock DB that returns 0 for sector concentration query."""
    db = AsyncMock()
    result = AsyncMock()
    result.scalar_one = MagicMock(return_value=0)
    db.execute = AsyncMock(return_value=result)
    return db


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_gate_passes_clean_signal():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
async def test_gate_blocks_non_buy_sell():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(action="HOLD"), db, _Settings())
    assert reason is not None
    assert "not BUY/SELL" in reason


@pytest.mark.asyncio
async def test_gate_blocks_low_global_confidence():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(confidence=40.0), db, _Settings())
    assert reason is not None
    assert "global floor" in reason


@pytest.mark.asyncio
async def test_gate_blocks_intraday_below_floor():
    """Intraday is disabled (floor=999) — all intraday signals blocked."""
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="intraday", confidence=65.0), db, _Settings())
    assert reason is not None
    assert "floored" in reason or "disabled" in reason

@pytest.mark.asyncio
async def test_gate_blocks_intraday_above_old_floor():
    """Intraday disabled at floor=999 — even high confidence signals are blocked.
    Live data: 34.8% WR, Sharpe -1.88 (May 2026). Disabled pending re-calibration."""
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="intraday", confidence=70.0), db, _Settings())
    assert reason is not None
    assert "floored" in reason or "disabled" in reason


@pytest.mark.asyncio
async def test_gate_blocks_swing_below_62():
    """Swing floor lowered to 62% (adjusted for new 65% confidence ceiling)."""
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="swing", confidence=61.0), db, _Settings())
    assert reason is not None


@pytest.mark.asyncio
async def test_gate_allows_swing_at_62():
    """Swing signals at ≥62% pass the style floor."""
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="swing", confidence=63.0), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
@pytest.mark.parametrize("sector", ["XLF", "XLP", "XLU"])
async def test_gate_blocks_restricted_sectors(sector):
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(sectorEtf=sector), db, _Settings())
    assert reason is not None
    assert "blocked" in reason


@pytest.mark.asyncio
async def test_gate_allows_unblocked_sector():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(sectorEtf="XLK"), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
async def test_gate_blocks_pre_earnings():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(daysToEarnings=1), db, _Settings())
    assert reason is not None
    assert "earnings" in reason.lower()


@pytest.mark.asyncio
async def test_gate_allows_post_earnings_window():
    """daysToEarnings > 2 is fine; 0 also fine (post-event)."""
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(daysToEarnings=0), db, _Settings())
    assert reason is None
    reason2, _ = await check_delivery_gates(_sig(daysToEarnings=5), db, _Settings())
    assert reason2 is None


@pytest.mark.asyncio
async def test_gate_blocks_low_profit_target():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    # profit_pct = (101 - 100) / 100 * 100 = 1% < 2%
    reason, _ = await check_delivery_gates(_sig(entry=100.0, target=101.0), db, _Settings())
    assert reason is not None
    assert "profit" in reason


@pytest.mark.asyncio
async def test_gate_blocks_sector_concentration():
    """Sector concentration: 2 BUY sends in 24h blocks the signal."""
    from services.delivery_gates import check_delivery_gates

    # DB mock returns concentration count = 2
    db = AsyncMock()
    conc_result = AsyncMock()
    conc_result.scalar_one = MagicMock(return_value=2)
    db.execute = AsyncMock(return_value=conc_result)

    # Patch the inner AsyncSessionLocal used by the adaptive floor gate
    mock_session = AsyncMock()
    mock_adb_result = AsyncMock()
    mock_adb_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_adb_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(_sig(sectorEtf="XLI"), db, _Settings())

    assert reason is not None
    assert "24h" in reason


@pytest.mark.asyncio
async def test_gate_blocks_insufficient_non_ta_sources():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    # Only technical sources — not enough for position
    reason, _ = await check_delivery_gates(
        _sig(sources=["Technical", "Backtest"]), db, _Settings()
    )
    assert reason is not None
    assert "non-TA" in reason


@pytest.mark.asyncio
async def test_gate_allows_position_with_two_non_ta():
    from services.delivery_gates import check_delivery_gates
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(
        _sig(style="position", sources=["Options", "13F", "Macro"]), db, _Settings()
    )
    assert reason is None
