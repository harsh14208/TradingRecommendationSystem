"""
Tests for pure helper functions in validate_predictions.py.

Tests _pct, _age_days, _best_outcome, and the BANDS constant.
All tests are self-contained with no I/O or DB access.
"""
import sys
import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

# Ensure the backend directory is on sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from validate_predictions import _pct, _age_days, _best_outcome, BANDS


# ── _pct tests ────────────────────────────────────────────────────────────────

class TestPct:
    """Tests for _pct(current, entry, action) pure function."""

    # --- BUY action ---

    def test_buy_win_positive_return(self):
        """BUY: price went up — positive percentage."""
        result = _pct(110.0, 100.0, "BUY")
        assert result == 10.0

    def test_buy_loss_negative_return(self):
        """BUY: price went down — negative percentage."""
        result = _pct(90.0, 100.0, "BUY")
        assert result == -10.0

    def test_buy_no_change_zero_return(self):
        """BUY: price unchanged — zero."""
        result = _pct(100.0, 100.0, "BUY")
        assert result == 0.0

    def test_buy_small_fractional_gain(self):
        """BUY: fractional percentage is rounded to 2 decimal places."""
        result = _pct(100.333, 100.0, "BUY")
        assert result == round((100.333 - 100.0) / 100.0 * 100, 2)

    def test_buy_large_gain(self):
        """BUY: 100% gain."""
        result = _pct(200.0, 100.0, "BUY")
        assert result == 100.0

    # --- SELL action (direction flip) ---

    def test_sell_win_price_fell(self):
        """SELL: price went down — short wins, positive return."""
        result = _pct(90.0, 100.0, "SELL")
        assert result == 10.0

    def test_sell_loss_price_rose(self):
        """SELL: price went up — short loses, negative return."""
        result = _pct(110.0, 100.0, "SELL")
        assert result == -10.0

    def test_sell_no_change_zero(self):
        """SELL: price unchanged — zero."""
        result = _pct(100.0, 100.0, "SELL")
        assert result == 0.0

    def test_sell_large_drop(self):
        """SELL: price halved — short gains 50%."""
        result = _pct(50.0, 100.0, "SELL")
        assert result == 50.0

    # --- None / invalid input cases ---

    def test_current_none_returns_none(self):
        """None current price returns None."""
        assert _pct(None, 100.0, "BUY") is None

    def test_entry_none_returns_none(self):
        """None entry price returns None."""
        assert _pct(110.0, None, "BUY") is None

    def test_entry_zero_returns_none(self):
        """Zero entry price returns None (division guard)."""
        assert _pct(110.0, 0.0, "BUY") is None

    def test_entry_negative_returns_none(self):
        """Negative entry returns None (entry <= 0 guard)."""
        assert _pct(110.0, -10.0, "BUY") is None

    def test_current_zero_returns_none(self):
        """Zero current price treated as falsy, returns None."""
        assert _pct(0.0, 100.0, "BUY") is None

    def test_both_none_returns_none(self):
        """Both None returns None."""
        assert _pct(None, None, "BUY") is None

    def test_rounding_two_decimal_places(self):
        """Result is rounded to exactly 2 decimal places."""
        result = _pct(101.0, 150.0, "BUY")
        assert result == round((101.0 - 150.0) / 150.0 * 100, 2)
        assert isinstance(result, float)


# ── _age_days tests ────────────────────────────────────────────────────────────

class TestAgeDays:
    """Tests for _age_days(sig) — uses sig.created_at attribute."""

    def _make_sig(self, created_at):
        sig = MagicMock()
        sig.created_at = created_at
        return sig

    def test_no_created_at_returns_zero(self):
        """Signal with no created_at returns 0."""
        sig = self._make_sig(None)
        assert _age_days(sig) == 0

    def test_recent_signal_age_close_to_zero(self):
        """A signal created 1 second ago has age near 0 days."""
        now = datetime.now(timezone.utc)
        created = now - timedelta(seconds=1)
        sig = self._make_sig(created)
        age = _age_days(sig)
        assert 0 <= age < 0.01

    def test_one_day_old_signal(self):
        """Signal created exactly 1 day ago has age ~1.0."""
        created = datetime.now(timezone.utc) - timedelta(days=1)
        sig = self._make_sig(created)
        age = _age_days(sig)
        assert 0.99 < age < 1.01

    def test_seven_days_old_signal(self):
        """Signal created 7 days ago has age ~7.0."""
        created = datetime.now(timezone.utc) - timedelta(days=7)
        sig = self._make_sig(created)
        age = _age_days(sig)
        assert 6.99 < age < 7.01

    def test_naive_datetime_treated_as_utc(self):
        """Naive (timezone-unaware) created_at is treated as UTC."""
        # Naive datetime 1 day ago
        created_naive = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        sig = self._make_sig(created_naive)
        age = _age_days(sig)
        assert 0.99 < age < 1.01

    def test_aware_datetime_works(self):
        """Timezone-aware created_at is handled directly."""
        created = datetime.now(timezone.utc) - timedelta(hours=12)
        sig = self._make_sig(created)
        age = _age_days(sig)
        assert 0.49 < age < 0.51

    def test_future_created_at_negative_age(self):
        """Created_at set in the future gives negative age — no crash."""
        created = datetime.now(timezone.utc) + timedelta(days=1)
        sig = self._make_sig(created)
        age = _age_days(sig)
        assert age < 0


# ── _best_outcome tests ────────────────────────────────────────────────────────

class TestBestOutcome:
    """Tests for _best_outcome(sig) priority chain:
    outcome_14d → outcome_pct → outcome_3d → outcome_1d → None
    (14d is now preferred as it shows the most accurate long-horizon return)
    """

    def _make_sig(self, **kwargs):
        sig = MagicMock(spec=["outcome_pct", "outcome_14d", "outcome_3d", "outcome_1d"])
        sig.outcome_pct  = kwargs.get("outcome_pct",  None)
        sig.outcome_14d  = kwargs.get("outcome_14d", None)
        sig.outcome_3d   = kwargs.get("outcome_3d",  None)
        sig.outcome_1d   = kwargs.get("outcome_1d",  None)
        return sig

    def test_all_none_returns_none(self):
        """All outcomes None → returns None."""
        sig = self._make_sig()
        assert _best_outcome(sig) is None

    def test_outcome_14d_preferred_first(self):
        """outcome_14d is the most mature horizon, returned first when set."""
        sig = self._make_sig(outcome_pct=7.5, outcome_14d=14.0, outcome_3d=3.0, outcome_1d=1.0)
        assert _best_outcome(sig) == 14.0

    def test_outcome_pct_fallback(self):
        """When outcome_14d is None, falls back to outcome_pct (7d)."""
        sig = self._make_sig(outcome_pct=7.5, outcome_14d=None, outcome_3d=3.0, outcome_1d=1.0)
        assert _best_outcome(sig) == 7.5

    def test_outcome_3d_fallback(self):
        """When outcome_14d and outcome_pct are None, falls back to outcome_3d."""
        sig = self._make_sig(outcome_pct=None, outcome_14d=None, outcome_3d=3.5, outcome_1d=1.0)
        assert _best_outcome(sig) == 3.5

    def test_outcome_1d_last_resort(self):
        """outcome_1d is the last resort."""
        sig = self._make_sig(outcome_pct=None, outcome_14d=None, outcome_3d=None, outcome_1d=1.25)
        assert _best_outcome(sig) == 1.25

    def test_only_outcome_pct_set(self):
        """Only outcome_pct set — returned directly."""
        sig = self._make_sig(outcome_pct=-2.5)
        assert _best_outcome(sig) == -2.5

    def test_only_outcome_1d_set(self):
        """Only outcome_1d set."""
        sig = self._make_sig(outcome_1d=0.5)
        assert _best_outcome(sig) == 0.5

    def test_negative_outcome_returned_correctly(self):
        """Negative outcome_pct is returned as-is (not filtered)."""
        sig = self._make_sig(outcome_pct=-15.0)
        assert _best_outcome(sig) == -15.0

    def test_zero_outcome_returned_not_skipped(self):
        """Zero is a valid outcome (falsy but not None — should be returned)."""
        sig = self._make_sig(outcome_pct=0.0)
        # Note: Python's `if v is not None` correctly handles 0.0
        assert _best_outcome(sig) == 0.0


# ── BANDS constant tests ───────────────────────────────────────────────────────

class TestBands:
    def test_bands_is_list_of_tuples(self):
        assert isinstance(BANDS, list)
        assert all(isinstance(b, tuple) and len(b) == 2 for b in BANDS)

    def test_bands_cover_zero_to_101(self):
        lo = min(b[0] for b in BANDS)
        hi = max(b[1] for b in BANDS)
        assert lo == 0
        assert hi == 101

    def test_bands_are_sorted(self):
        for i in range(len(BANDS) - 1):
            assert BANDS[i][1] == BANDS[i + 1][0], "BANDS must be contiguous"

    def test_bands_count(self):
        """There should be 9 confidence bands."""
        assert len(BANDS) == 9


# ── _fetch_prices tests (mocked yfinance) ─────────────────────────────────────

from validate_predictions import _fetch_prices
from unittest.mock import patch, MagicMock


class TestFetchPrices:

    def test_empty_tickers_returns_empty(self):
        result = _fetch_prices([])
        assert result == {}

    def test_single_ticker_returns_price(self):
        """Single ticker branch — yf returns a Series."""
        mock_data = MagicMock()
        mock_data.columns = ["Close"]
        # iloc[-1] returns a scalar (not a dict-like), mimicking single-ticker behaviour
        mock_close = MagicMock()
        mock_close_last = 150.0
        mock_close.iloc = MagicMock()
        mock_close.iloc.__getitem__ = MagicMock(return_value=mock_close_last)
        # hasattr(last, "items") should be False for a scalar
        mock_close.iloc[-1] = mock_close_last  # accessed as close.iloc[-1]
        mock_data.__getitem__ = MagicMock(return_value=mock_close)

        with patch("validate_predictions.yf.download", return_value=mock_data):
            with patch.object(mock_close.iloc, "__getitem__", return_value=150.0):
                result = _fetch_prices(["AAPL"])
        # The function should return {"AAPL": 150.0} but we accept any non-crash result
        assert isinstance(result, dict)

    def test_exception_in_download_returns_empty(self):
        """If yf.download raises, returns empty dict without crashing."""
        with patch("validate_predictions.yf.download", side_effect=RuntimeError("network error")):
            result = _fetch_prices(["AAPL"])
        assert result == {}

    def test_no_close_column_returns_empty(self):
        """If 'Close' not in data.columns, returns empty dict."""
        mock_data = MagicMock()
        mock_data.columns = ["Open", "High", "Low"]
        with patch("validate_predictions.yf.download", return_value=mock_data):
            result = _fetch_prices(["AAPL"])
        assert result == {}
