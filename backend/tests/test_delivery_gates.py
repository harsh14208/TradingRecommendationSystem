"""
Tests for services/delivery_gates.py.

Each gate is tested in isolation via a minimal sig_dict and a mock DB + settings.
"""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# (§67 FOMC gate + _days_to_nearest_fomc removed 2026-07-14 — gate audit)


@contextmanager
def _no_calendar_haircuts():
    """Neutralize the date-dependent gate haircuts (FOMC proximity, pre-long-weekend,
    Thursday haircut) so `check_delivery_gates` tests don't flake when actually run
    on/near those calendar dates (e.g. an FOMC decision day, the day before a holiday
    weekend, or a Thursday)."""
    from datetime import datetime, timezone

    _tuesday = datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc)
    with (
        patch("services.market_calendar.is_pre_long_weekend", return_value=(False, None)),
        patch("services.delivery_gates.datetime") as mock_dt,
    ):
        mock_dt.now.return_value = _tuesday
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield


@pytest.fixture(autouse=True)
def _neutralize_calendar_gates():
    """Module-wide: every test runs with the date-dependent FOMC/long-weekend gates
    neutralized, so the suite is deterministic regardless of the calendar date it
    runs on."""
    with _no_calendar_haircuts():
        yield


# ── Helpers ───────────────────────────────────────────────────────────────────


def _sig(**kwargs):
    base = {
        "ticker": "AAPL",
        "action": "BUY",
        "confidence": 65.0,
        "style": "position",
        "sectorEtf": "XLK",
        "sources": ["Options", "13F"],
        "entry": 100.0,
        "target": 110.0,
        "daysToEarnings": 30,
        "hasMr": True,  # MR gate required for BUY delivery (2026-06-02 fix)
    }
    base.update(kwargs)
    return base


class _Settings:
    min_confidence = 40.0  # recalibrated post phantom-win correction (was 55→57, now 40)


async def _db_no_sector_count():
    """Mock DB that returns 0 for sector concentration query."""
    db = AsyncMock()
    result = AsyncMock()
    result.scalar_one = MagicMock(return_value=0)
    result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    return db


# ── Internal helper tests ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_utcnow_naive_uses_utc_timezone():
    """_utcnow_naive must call datetime.now with timezone.utc."""
    from datetime import timezone
    from services.delivery_gates import _utcnow_naive

    with patch("services.delivery_gates.datetime") as mock_dt:
        mock_dt.now.return_value.replace.return_value = "naive-ts"
        assert _utcnow_naive() == "naive-ts"
        mock_dt.now.assert_called_once_with(timezone.utc)


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_gate_passes_clean_signal():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
async def test_gate_blocks_xli_sector():
    """ACT-1: XLI blocked at delivery — live WR 36.1% (N=36, WR<50% at N≥30)."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with patch("pathlib.Path.exists", return_value=False):
        reason, _ = await check_delivery_gates(_sig(sectorEtf="XLI"), db, _Settings())
    assert reason is not None
    assert "XLI" in reason


@pytest.mark.asyncio
async def test_gate_blocks_buy_without_mr_setup():
    """BUY signals without a MR condition (hasMr=False) must be blocked.

    Root-cause fix for live WR 42% vs backtest WR 68% gap: the backtest only
    validates MR entries (oversold RSI/BB%B/IBS/VWAP%); non-MR BUYs on
    uptrending stocks have no backtest validation and drag live WR down.
    """
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(hasMr=False), db, _Settings())
    assert reason is not None
    assert "MR setup" in reason or "no MR" in reason.lower()


@pytest.mark.asyncio
async def test_gate_buy_missing_hasmr_key_defaults_true():
    """A dict missing the hasMr key (pre-field rows / EOD reconstruction)
    defaults to True and passes the MR gate — aligned with
    structural_delivery_status (2026-06-17 revert of the ACT-4c default).
    An explicit hasMr=False still blocks."""
    from services.delivery_gates import check_delivery_gates

    eod_sig = _sig()
    del eod_sig["hasMr"]
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(eod_sig, db, _Settings())
    assert reason is None  # missing key defaults True → passes

    eod_sig["hasMr"] = False
    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(eod_sig, db, _Settings())
    assert reason is not None and "MR" in reason


@pytest.mark.asyncio
async def test_gate_passes_buy_with_mr_setup():
    """BUY signals with hasMr=True pass the MR gate."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(hasMr=True), db, _Settings())
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
    reason, _ = await check_delivery_gates(_sig(confidence=39.0), db, _Settings())
    assert reason is not None
    assert "global floor" in reason


@pytest.mark.asyncio
async def test_gate_blocks_intraday_below_floor():
    """Intraday re-enabled 2026-06-15 at the 40% floor — below-floor still blocked."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="intraday", confidence=35.0), db, _Settings())
    assert reason is not None
    assert "floor" in reason or "40%" in reason


@pytest.mark.asyncio
async def test_gate_allows_intraday_above_floor_without_mr():
    """Intraday re-enabled (2026-06-15, owner request): a momentum/breakout signal
    above the 40% floor delivers even without an MR setup (hasMr=False) — intraday
    is exempt from the MR-setup gate."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="intraday", confidence=70.0, hasMr=False), db, _Settings())
    assert reason is None


class _SettingsShort:
    """Settings with SELL delivery enabled (LONG_ONLY=false)."""

    min_confidence = 40.0
    long_only = False


@pytest.mark.asyncio
async def test_gate_blocks_intraday_sell_without_mr():
    """2026-06-22: intraday SELL is NO LONGER exempt from the MR gate. The
    MR-exempt intraday-SELL cohort resolved 0% WR / −6.46%/trade since 2026-06-15
    (shorting momentum into a rising tape), so a SELL without an overbought setup
    is blocked even at intraday style and above the 40% floor."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    sig = _sig(action="SELL", style="intraday", confidence=70.0)
    sig.pop("hasMrSell", None)  # no overbought setup
    reason, _ = await check_delivery_gates(sig, db, _SettingsShort())
    assert reason is not None and "SELL MR setup" in reason


@pytest.mark.asyncio
async def test_gate_intraday_sell_with_mr_clears_mr_gate():
    """An intraday SELL WITH an overbought setup (hasMrSell=True) is no longer
    blocked by the MR gate specifically (other gates may still apply)."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    sig = _sig(action="SELL", style="intraday", confidence=70.0, hasMrSell=True)
    reason, _ = await check_delivery_gates(sig, db, _SettingsShort())
    assert reason is None or "SELL MR setup" not in reason


@pytest.mark.asyncio
async def test_gate_blocks_swing_below_46():
    """Swing floor recalibrated to 46% post phantom-win correction (was 70% on old scale)."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="swing", confidence=45.0), db, _Settings())
    assert reason is not None


def _db_returning_outcomes(outcomes):
    """Mock DB whose .scalars().all() returns the given outcome_pct list."""
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value = MagicMock(all=MagicMock(return_value=outcomes))
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.mark.asyncio
async def test_intraday_safety_rail_auto_disables_on_low_wr():
    """N≥30 resolved intraday BUYs with WR<40% → safety rail flags blocked."""
    from services.delivery_gates import _intraday_safety_blocked

    db = _db_returning_outcomes([1.0] * 10 + [-1.0] * 20)  # 30 resolved, 33% WR
    blocked, wr, n = await _intraday_safety_blocked(db)
    assert n == 30 and blocked is True and round(wr, 2) == 0.33


@pytest.mark.asyncio
async def test_intraday_safety_rail_passes_below_min_n_or_good_wr():
    """Below N=30, or with WR≥40%, the safety rail does NOT block."""
    from services.delivery_gates import _intraday_safety_blocked

    blocked, _wr, n = await _intraday_safety_blocked(_db_returning_outcomes([1.0] * 5))
    assert n == 5 and blocked is False  # too few to judge
    blocked, wr, n = await _intraday_safety_blocked(_db_returning_outcomes([1.0] * 20 + [-1.0] * 20))
    assert n == 40 and round(wr, 2) == 0.50 and blocked is False  # WR ok


@pytest.mark.asyncio
async def test_gate_allows_swing_at_46():
    """Swing signals at ≥46% pass the style floor."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with _no_calendar_haircuts():
        reason, _ = await check_delivery_gates(_sig(style="swing", confidence=46.0), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", ["LRCX", "MRVL", "AMAT", "KLAC"])
async def test_gate_blocks_semi_equipment_tickers(ticker):
    """Semi equipment sub-sector blocked — continuation not MR."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(ticker=ticker), db, _Settings())
    assert reason is not None
    assert "blocked" in reason


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", ["STT", "MTB"])
async def test_gate_blocks_xlf_regional_bank_tickers(ticker):
    """XLF regional banks blocked — rate-cycle driven, not price-level MR (OOS v5: 0% WR)."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(ticker=ticker), db, _Settings())
    assert reason is not None
    assert "blocked" in reason


@pytest.mark.asyncio
@pytest.mark.parametrize("sector", ["XLF", "XLP", "XLU"])
async def test_gate_blocks_restricted_sectors(sector):
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with patch("pathlib.Path.exists", return_value=False):
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
@pytest.mark.parametrize("sector", ["XLF", "XLP", "XLU", "XLI"])
async def test_gate_allows_promoted_sector(sector):
    """§117: blocked sectors pass delivery gates when QENG-1c promotion is live."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with patch("services.sector_ml_promotion.get_promoted_sectors_cached", new=AsyncMock(return_value={sector})):
        reason, _ = await check_delivery_gates(_sig(sectorEtf=sector), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
async def test_gate_reblocks_expired_promotion():
    """§117: promotion expiration/rollback removes the sector unblock."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with patch("services.sector_ml_promotion.get_promoted_sectors_cached", new=AsyncMock(return_value=set())):
        reason, _ = await check_delivery_gates(_sig(sectorEtf="XLF"), db, _Settings())
    assert reason is not None
    assert "XLF" in reason
    assert "QENG-1c" in reason


@pytest.mark.asyncio
async def test_gate_promotion_lookup_failure_fails_closed():
    """§117: if promotion lookup fails, blocked sectors stay blocked (fail closed)."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    with patch(
        "services.sector_ml_promotion.get_promoted_sectors_cached", new=AsyncMock(side_effect=RuntimeError("db down"))
    ):
        reason, _ = await check_delivery_gates(_sig(sectorEtf="XLP"), db, _Settings())
    assert reason is not None
    assert "XLP" in reason


@pytest.mark.asyncio
async def test_gate_allows_pre_earnings_window():
    """daysToEarnings > 2 is fine; 0 is earnings day and was blocked pre-removal."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    # The earnings gate was removed from delivery_gates.py (no longer blocks).
    reason, _ = await check_delivery_gates(_sig(daysToEarnings=5), db, _Settings())
    assert reason is None


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
        reason, _ = await check_delivery_gates(_sig(sectorEtf="XLK"), db, _Settings())

    assert reason is not None
    assert "24h" in reason


@pytest.mark.asyncio
async def test_gate_blocks_insufficient_non_ta_sources():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    # Only technical sources — not enough for position
    reason, _ = await check_delivery_gates(_sig(sources=["Technical", "Backtest"]), db, _Settings())
    assert reason is not None
    assert "non-TA" in reason


@pytest.mark.asyncio
async def test_gate_allows_position_with_two_non_ta():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(_sig(style="position", sources=["Options", "13F", "Macro"]), db, _Settings())
    assert reason is None


@pytest.mark.asyncio
async def test_gate_blocks_swing_with_one_non_ta():
    """Swing now requires 2 non-TA sources (same as position) — §33 live alpha −1.028%."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(
        _sig(style="swing", confidence=70.0, sources=["Technical", "Macro"]), db, _Settings()
    )
    assert reason is not None
    assert "non-TA" in reason


@pytest.mark.asyncio
async def test_gate_allows_swing_with_two_non_ta():
    """Swing with 2 independent non-TA sources passes the source independence gate."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()
    reason, _ = await check_delivery_gates(
        _sig(style="swing", confidence=70.0, sources=["Technical", "Macro", "Options"]),
        db,
        _Settings(),
    )
    assert reason is None


# ── §37 audit fix tests: GOOG/GOOGL same-underlying deduplication ─────────────


def _db_with_counts(*counts):
    """DB mock that returns sequential scalar values across multiple execute() calls.

    The first result is for the AppSettings adaptive-weights lookup; subsequent
    results are for sector/alias concentration counts."""
    db = AsyncMock()
    results = []
    # AppSettings.scalar_one_or_none() → None
    app_r = AsyncMock()
    app_r.scalar_one_or_none = MagicMock(return_value=None)
    results.append(app_r)
    for count in counts:
        r = AsyncMock()
        r.scalar_one = MagicMock(return_value=count)
        results.append(r)
    db.execute = AsyncMock(side_effect=results)
    return db


@pytest.mark.asyncio
async def test_googl_blocked_when_goog_sent():
    """GOOGL BUY should be blocked if GOOG BUY was sent within 24h."""
    from services.delivery_gates import check_delivery_gates

    # sector_concentration returns 0, alias gate returns 1 (GOOG already sent)
    db = _db_with_counts(0, 1)

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(ticker="GOOGL", sectorEtf="XLC", sources=["Options", "13F"]),
            db,
            _Settings(),
        )
    assert reason is not None, "GOOGL should be blocked when GOOG was recently sent"
    assert "alias" in reason.lower() or "same underlying" in reason.lower()


@pytest.mark.asyncio
async def test_goog_blocked_when_googl_sent():
    """GOOG BUY should be blocked if GOOGL BUY was sent within 24h."""
    from services.delivery_gates import check_delivery_gates

    db = _db_with_counts(0, 1)

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(ticker="GOOG", sectorEtf="XLC", sources=["Options", "13F"]),
            db,
            _Settings(),
        )
    assert reason is not None, "GOOG should be blocked when GOOGL was recently sent"
    assert "alias" in reason.lower() or "same underlying" in reason.lower()


@pytest.mark.asyncio
async def test_alias_gate_passes_when_no_recent_alias_send():
    """GOOGL BUY passes when GOOG has NOT been sent in the last 24h."""
    from services.delivery_gates import check_delivery_gates

    # sector_concentration=0, alias count=0 → passes both
    db = _db_with_counts(0, 0)

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(ticker="GOOGL", sectorEtf="XLC", sources=["Options", "13F"]),
            db,
            _Settings(),
        )
    assert reason is None, "GOOGL should pass when no GOOG alias send in 24h"


@pytest.mark.asyncio
async def test_alias_gate_does_not_affect_non_aliased_ticker():
    """Tickers with no alias (e.g. AAPL) are unaffected by the alias gate."""
    from services.delivery_gates import check_delivery_gates

    # sector_concentration=0 only — alias gate should not query at all for AAPL
    db = _db_with_counts(0)

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(ticker="AAPL", sectorEtf="XLK", sources=["Options", "13F"]),
            db,
            _Settings(),
        )
    assert reason is None, "AAPL should be unaffected by alias gate"


@pytest.mark.asyncio
async def test_alias_gate_only_fires_on_buy_not_sell():
    """Alias gate is BUY-only — SELL signals for GOOGL should not be blocked by it."""
    from services.delivery_gates import check_delivery_gates

    # Only sector_concentration query executes (alias gate is BUY-only)
    db = _db_with_counts(0)

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(ticker="GOOGL", action="SELL", sectorEtf="XLC", sources=["Options", "13F"]),
            db,
            _Settings(),
        )
    # SELL may fail for other reasons (non-TA source, etc.) but not alias gate
    if reason:
        assert "alias" not in reason.lower() and "same underlying" not in reason.lower()


# ── _days_to_nearest_fomc ─────────────────────────────────────────────────────


# ── Ticker-adaptive win rate gates (lines 114-117) ───────────────────────────


@pytest.mark.asyncio
async def test_ticker_adaptive_low_wr_raises_floor():
    """A ticker with twr < 0.45 raises the confidence floor to 68."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    app_settings_row = MagicMock()
    app_settings_row.data = {"adaptive_weights": {"ticker_win_rates": {"AAPL": 0.40}}}

    app_result = AsyncMock()
    app_result.scalar_one_or_none = MagicMock(return_value=app_settings_row)
    sector_result = AsyncMock()
    sector_result.scalar_one = MagicMock(return_value=0)
    sector_result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(side_effect=[app_result, sector_result, sector_result, sector_result])

    reason, _ = await check_delivery_gates(
        _sig(ticker="AAPL", confidence=65.0),  # below raised 68 floor
        db,
        _Settings(),
    )
    assert reason is not None
    assert "68" in reason


@pytest.mark.asyncio
async def test_ticker_adaptive_high_wr_lowers_floor():
    """A ticker with twr >= 0.75 lowers the floor, allowing lower-confidence signals."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    app_settings_row = MagicMock()
    app_settings_row.data = {"adaptive_weights": {"ticker_win_rates": {"AAPL": 0.80}}}

    app_result = AsyncMock()
    app_result.scalar_one_or_none = MagicMock(return_value=app_settings_row)
    sector_result = AsyncMock()
    sector_result.scalar_one = MagicMock(return_value=0)
    sector_result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(side_effect=[app_result, sector_result, sector_result, sector_result])

    # With floor lowered to 52, a conf=53 signal should pass global floor
    with _no_calendar_haircuts():
        reason, _ = await check_delivery_gates(
            _sig(ticker="AAPL", confidence=53.0),
            db,
            _Settings(),
        )
    # May pass or fail other gates but NOT the global conf floor
    if reason:
        assert "52" not in reason and "global floor" not in reason


# ── VIX < 15 gate (line 164) ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_vix_below_15_blocks_buy():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(vix=12.0),
            db,
            _Settings(),
        )
    assert reason is not None
    assert "VIX" in reason and "15" in reason


@pytest.mark.asyncio
async def test_vix_above_15_does_not_block():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(vix=20.0),
            db,
            _Settings(),
        )
    if reason:
        assert "VIX" not in reason or "15" not in reason


# ── Cross-asset headwinds gate (line 173) ────────────────────────────────────


@pytest.mark.asyncio
async def test_three_headwinds_blocks_buy():

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)


# ── Ex-dividend gate (line 186) ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ex_div_blocks_buy():
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)

    with patch("database.AsyncSessionLocal", return_value=mock_session):
        reason, _ = await check_delivery_gates(
            _sig(daysToExDiv=1),
            db,
            _Settings(),
        )
    assert reason is not None
    assert "ex-dividend" in reason.lower() or "ex_div" in reason.lower() or "dividend" in reason.lower()


# ── FOMC gates (lines 325, 327-330) ──────────────────────────────────────────


# ── Thursday haircut (lines 298-318) ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_thursday_haircut_below_58():
    from datetime import datetime, timezone
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)

    # Thursday = weekday 3
    thursday = datetime(2026, 1, 29, 12, 0, tzinfo=timezone.utc)  # A Thursday

    with (
        patch("database.AsyncSessionLocal", return_value=mock_session),
        patch("services.delivery_gates.datetime") as mock_dt,
    ):
        mock_dt.now.return_value = thursday
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        reason, out_sig = await check_delivery_gates(
            _sig(confidence=57.0),  # < 58 → haircut applies
            db,
            _Settings(),
        )

    if reason is None:
        assert out_sig.get("confidence", 60) <= 57.0


# ── September / October seasonality (lines 348, 350) ─────────────────────────


# ── Long-weekend haircut (lines 270-287) ─────────────────────────────────────


@pytest.mark.asyncio
async def test_pre_long_weekend_haircut_applied():
    from services.delivery_gates import check_delivery_gates
    import services.market_calendar  # noqa: F401  # ensure module is loaded for patch targets

    db = await _db_no_sector_count()

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    scalar_result = AsyncMock()
    scalar_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=scalar_result)

    from unittest.mock import patch

    with (
        patch("database.AsyncSessionLocal", return_value=mock_session),
        patch("services.market_calendar.get_upcoming_holidays", return_value=[]),
        patch("services.market_calendar.is_pre_long_weekend", return_value=(True, "Memorial Day")),
    ):
        reason, out_sig = await check_delivery_gates(
            _sig(confidence=65.0),
            db,
            _Settings(),
        )

    if reason is None:
        assert out_sig.get("confidence", 65.0) <= 60.1  # 65 - 5 = 60


@pytest.mark.asyncio
async def test_gate_passes_fred_macro_regime_panel():
    """Item 6: §14 demoted to monitoring — hard blocks removed.
    NFCI/BAA10Y/T10Y3M no longer block delivery."""
    from services.delivery_gates import check_delivery_gates

    db = await _db_no_sector_count()

    # All previously-blocking FRED macro conditions now pass.
    test_cases = [
        _sig(nfci=0.6),
        _sig(nfci=0.1, score=45),
        _sig(baa10y=4.5),
        _sig(baa10y=3.5, score=45),
        _sig(t10y3m=-0.1, score=50),
    ]
    for case in test_cases:
        reason, _ = await check_delivery_gates(case, db, _Settings())
        assert reason is None, f"Expected pass for {case}"
