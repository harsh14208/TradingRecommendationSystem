"""
Tests for pure/sync functions in services/scanner.py:
  - _market_session()
  - _market_hours_ok()
  - _pct()
  - _check_data_quality()
  - _today_start_utc()

All external imports inside scanner.py (aiohttp, models, services.*) are patched
at module level so the file can be imported without real infrastructure.
"""
import sys
import os
import pytest
from datetime import datetime, time as dtime
from unittest.mock import MagicMock, patch, PropertyMock
import pytz

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

_ET = pytz.timezone("America/New_York")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _et_dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    """Return an ET-aware datetime for today at the given time."""
    return _ET.localize(datetime(2024, 1, 15, hour, minute, second))


def _make_good_df():
    """Return a minimal DataFrame-like mock that passes quality checks."""
    df = MagicMock()
    df.__len__ = MagicMock(return_value=10)
    close_series = MagicMock()
    close_series.iloc.__getitem__ = MagicMock(return_value=150.0)
    df.__getitem__ = MagicMock(return_value=close_series)
    return df


def _make_bad_df(reason="none"):
    """Return a DataFrame-like mock that fails quality checks."""
    if reason == "none":
        return None
    if reason == "short":
        df = MagicMock()
        df.__len__ = MagicMock(return_value=2)
        return df
    if reason == "zero_close":
        df = MagicMock()
        df.__len__ = MagicMock(return_value=10)
        close_series = MagicMock()
        close_series.iloc.__getitem__ = MagicMock(return_value=0)
        df.__getitem__ = MagicMock(return_value=close_series)
        return df


# ── Import scanner with mocked heavy dependencies ─────────────────────────────

@pytest.fixture(autouse=True, scope="module")
def _mock_scanner_imports():
    """Patch all heavy imports that scanner.py tries at import time."""
    mocks = {
        "aiohttp":                      MagicMock(),
        "database":                     MagicMock(),
        "models":                       MagicMock(),
        "services.aaii":                MagicMock(),
        "services.breadth":             MagicMock(),
        "services.cot":                 MagicMock(),
        "services.fear_greed":          MagicMock(),
        "services.macro":               MagicMock(),
        "services.market_data":         MagicMock(),
        "services.signal_engine":       MagicMock(),
        "services.telegram_svc":        MagicMock(),
        "config":                       MagicMock(),
    }
    # config needs TIERS attribute
    mocks["config"].TIERS = ["free", "basic", "pro"]
    mocks["config"].get_settings = MagicMock(return_value=MagicMock())

    with patch.dict("sys.modules", mocks):
        # Remove scanner from cache so it re-imports with mocks
        sys.modules.pop("services.scanner", None)
        import services.scanner as scanner_module
        yield scanner_module
        sys.modules.pop("services.scanner", None)


# ── _market_session tests ─────────────────────────────────────────────────────

class TestMarketSession:

    def _call_session(self, scanner, et_dt):
        with patch.object(scanner, "datetime") as mock_dt_cls:
            mock_dt_cls.now.return_value = et_dt
            return scanner._market_session()

    def test_pre_market_start(self, _mock_scanner_imports):
        """4:00 ET → pre market."""
        result = self._call_session(_mock_scanner_imports, _et_dt(4, 0))
        assert result == "pre"

    def test_pre_market_mid(self, _mock_scanner_imports):
        """6:30 ET → pre market."""
        result = self._call_session(_mock_scanner_imports, _et_dt(6, 30))
        assert result == "pre"

    def test_pre_market_boundary(self, _mock_scanner_imports):
        """9:29 ET is still pre market (not yet regular)."""
        result = self._call_session(_mock_scanner_imports, _et_dt(9, 29))
        assert result == "pre"

    def test_regular_session_open(self, _mock_scanner_imports):
        """9:30 ET → regular session."""
        result = self._call_session(_mock_scanner_imports, _et_dt(9, 30))
        assert result == "regular"

    def test_regular_session_mid_day(self, _mock_scanner_imports):
        """12:00 ET → regular session."""
        result = self._call_session(_mock_scanner_imports, _et_dt(12, 0))
        assert result == "regular"

    def test_regular_session_close_boundary(self, _mock_scanner_imports):
        """15:59 ET is still regular (< 16:00)."""
        result = self._call_session(_mock_scanner_imports, _et_dt(15, 59))
        assert result == "regular"

    def test_after_hours_start(self, _mock_scanner_imports):
        """16:00 ET → after hours."""
        result = self._call_session(_mock_scanner_imports, _et_dt(16, 0))
        assert result == "after"

    def test_after_hours_mid(self, _mock_scanner_imports):
        """18:00 ET → after hours."""
        result = self._call_session(_mock_scanner_imports, _et_dt(18, 0))
        assert result == "after"

    def test_after_hours_boundary(self, _mock_scanner_imports):
        """19:59 ET → after hours (< 20:00)."""
        result = self._call_session(_mock_scanner_imports, _et_dt(19, 59))
        assert result == "after"

    def test_closed_late_evening(self, _mock_scanner_imports):
        """20:00 ET → closed."""
        result = self._call_session(_mock_scanner_imports, _et_dt(20, 0))
        assert result == "closed"

    def test_closed_midnight(self, _mock_scanner_imports):
        """0:00 ET → closed (before pre market)."""
        result = self._call_session(_mock_scanner_imports, _et_dt(0, 0))
        assert result == "closed"

    def test_closed_early_morning(self, _mock_scanner_imports):
        """3:59 ET → closed (before 4:00 pre)."""
        result = self._call_session(_mock_scanner_imports, _et_dt(3, 59))
        assert result == "closed"


# ── _market_hours_ok tests ─────────────────────────────────────────────────────

class TestMarketHoursOk:

    def _call_hours_ok(self, scanner, et_dt):
        with patch.object(scanner, "datetime") as mock_dt_cls:
            mock_dt_cls.now.return_value = et_dt
            return scanner._market_hours_ok()

    def test_before_open_returns_false(self, _mock_scanner_imports):
        """9:29 ET → not market hours."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(9, 29))
        assert result is False

    def test_at_open_returns_true(self, _mock_scanner_imports):
        """9:30 ET → market is open."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(9, 30))
        assert result is True

    def test_mid_day_returns_true(self, _mock_scanner_imports):
        """13:00 ET → market is open."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(13, 0))
        assert result is True

    def test_at_close_boundary_returns_true(self, _mock_scanner_imports):
        """15:55 ET is still in range (<=15:55)."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(15, 55))
        assert result is True

    def test_after_close_boundary_returns_false(self, _mock_scanner_imports):
        """15:56 ET → past clean market window."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(15, 56))
        assert result is False

    def test_after_hours_returns_false(self, _mock_scanner_imports):
        """17:00 ET → not market hours."""
        result = self._call_hours_ok(_mock_scanner_imports, _et_dt(17, 0))
        assert result is False

    def test_saturday_during_trading_time_returns_false(self, _mock_scanner_imports):
        """Saturday 10:00 ET → closed even though time is within 9:30–15:55."""
        ET = pytz.timezone("America/New_York")
        saturday = ET.localize(datetime(2024, 1, 13, 10, 0))  # 2024-01-13 is a Saturday
        result = self._call_hours_ok(_mock_scanner_imports, saturday)
        assert result is False

    def test_sunday_during_trading_time_returns_false(self, _mock_scanner_imports):
        """Sunday 13:00 ET → closed even though time is within 9:30–15:55."""
        ET = pytz.timezone("America/New_York")
        sunday = ET.localize(datetime(2024, 1, 14, 13, 0))  # 2024-01-14 is a Sunday
        result = self._call_hours_ok(_mock_scanner_imports, sunday)
        assert result is False


# ── _pct (scanner) tests ───────────────────────────────────────────────────────

class TestScannerPct:
    """The _pct in scanner.py is identical to validate_predictions._pct — test it directly."""

    def test_buy_gain(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(110.0, 100.0, "BUY") == 10.0

    def test_buy_loss(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(90.0, 100.0, "BUY") == -10.0

    def test_sell_gain_on_drop(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(90.0, 100.0, "SELL") == 10.0

    def test_sell_loss_on_rise(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(110.0, 100.0, "SELL") == -10.0

    def test_none_current_returns_none(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(None, 100.0, "BUY") is None

    def test_none_entry_returns_none(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(100.0, None, "BUY") is None

    def test_zero_entry_returns_none(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(100.0, 0.0, "BUY") is None

    def test_negative_entry_returns_none(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(100.0, -5.0, "BUY") is None

    def test_zero_current_returns_none(self, _mock_scanner_imports):
        assert _mock_scanner_imports._pct(0.0, 100.0, "BUY") is None


# ── _check_data_quality tests ─────────────────────────────────────────────────

class TestCheckDataQuality:
    """
    _check_data_quality uses module-level _data_quality dict.
    We reset it between tests to avoid cross-contamination.
    """

    def _reset_dq(self, scanner):
        scanner._data_quality.clear()

    def test_good_data_resets_counter(self, _mock_scanner_imports):
        s = _mock_scanner_imports
        self._reset_dq(s)
        # Pre-seed a bad count
        s._data_quality["AAPL"] = 3
        df = _make_good_df()
        result = s._check_data_quality({"AAPL": df}, MagicMock())
        assert s._data_quality["AAPL"] == 0
        assert "AAPL" not in result

    def test_none_df_increments_counter(self, _mock_scanner_imports):
        s = _mock_scanner_imports
        self._reset_dq(s)
        result = s._check_data_quality({"TSLA": None}, MagicMock())
        assert s._data_quality["TSLA"] == 1
        assert "TSLA" not in result  # counter is 1, not 5 yet

    def test_alert_exactly_at_five(self, _mock_scanner_imports):
        """Ticker is added to degraded list only when counter transitions to 5."""
        s = _mock_scanner_imports
        self._reset_dq(s)
        s._data_quality["MSFT"] = 4  # already at 4 consecutive failures
        result = s._check_data_quality({"MSFT": None}, MagicMock())
        assert s._data_quality["MSFT"] == 5
        assert "MSFT" in result

    def test_no_alert_at_four(self, _mock_scanner_imports):
        """Counter at 3, one more bad → 4, no alert yet."""
        s = _mock_scanner_imports
        self._reset_dq(s)
        s._data_quality["GOOG"] = 3
        result = s._check_data_quality({"GOOG": None}, MagicMock())
        assert s._data_quality["GOOG"] == 4
        assert "GOOG" not in result

    def test_no_repeat_alert_at_six(self, _mock_scanner_imports):
        """Counter at 5, one more bad → 6, no alert (only alerts on == 5)."""
        s = _mock_scanner_imports
        self._reset_dq(s)
        s._data_quality["NVDA"] = 5
        result = s._check_data_quality({"NVDA": None}, MagicMock())
        assert s._data_quality["NVDA"] == 6
        assert "NVDA" not in result

    def test_empty_histories_returns_empty(self, _mock_scanner_imports):
        s = _mock_scanner_imports
        self._reset_dq(s)
        result = s._check_data_quality({}, MagicMock())
        assert result == []

    def test_multiple_tickers_partial_bad(self, _mock_scanner_imports):
        """Only bad tickers increment; good tickers reset."""
        s = _mock_scanner_imports
        self._reset_dq(s)
        s._data_quality["BAD"] = 4
        s._data_quality["GOOD"] = 3
        histories = {
            "BAD":  None,
            "GOOD": _make_good_df(),
        }
        result = s._check_data_quality(histories, MagicMock())
        assert "BAD" in result
        assert s._data_quality["GOOD"] == 0

    def test_counter_accumulates_across_calls(self, _mock_scanner_imports):
        """Successive calls to _check_data_quality accumulate the counter."""
        s = _mock_scanner_imports
        self._reset_dq(s)
        settings = MagicMock()
        for _ in range(4):
            s._check_data_quality({"AMD": None}, settings)
        assert s._data_quality["AMD"] == 4
        result = s._check_data_quality({"AMD": None}, settings)
        assert s._data_quality["AMD"] == 5
        assert "AMD" in result


# ── _today_start_utc tests ────────────────────────────────────────────────────

class TestTodayStartUtc:

    def test_returns_datetime(self, _mock_scanner_imports):
        result = _mock_scanner_imports._today_start_utc()
        assert isinstance(result, datetime)

    def test_is_naive_datetime(self, _mock_scanner_imports):
        """Result should be timezone-naive (stripped to UTC)."""
        result = _mock_scanner_imports._today_start_utc()
        assert result.tzinfo is None

    def test_time_is_midnight_utc(self, _mock_scanner_imports):
        """Hour/minute/second/microsecond should be zero or very close
        (midnight ET expressed as UTC offset)."""
        result = _mock_scanner_imports._today_start_utc()
        # The result is midnight ET → some hour in UTC (4 or 5).
        # Just verify that minute, second, and microsecond are 0.
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0

    def test_is_before_current_utc(self, _mock_scanner_imports):
        """Midnight ET today should be before right now."""
        from datetime import timezone
        result = _mock_scanner_imports._today_start_utc()
        now_utc_naive = datetime.utcnow()
        assert result <= now_utc_naive
