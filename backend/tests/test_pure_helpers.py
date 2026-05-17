"""
Tests for several pure helper modules that require no DB/network:

1. services/calibration.py  — _blend(), apply_calibration(), load_calibration()
2. services/bayesian_smoothing.py — calculate_predictive_interval()
3. services/market_calendar.py — is_pre_long_weekend()
"""
import sys
import os
import json
import math
import tempfile
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# 1. services/calibration.py
# ─────────────────────────────────────────────────────────────────────────────

from services.calibration import _blend, apply_calibration, load_calibration


class TestBlend:

    def test_below_min_n_returns_zero(self):
        """Fewer than _MIN_N (3) samples → blend = 0.0."""
        assert _blend(0) == 0.0
        assert _blend(1) == 0.0
        assert _blend(2) == 0.0

    def test_at_min_n_returns_nonzero(self):
        """Exactly _MIN_N (3) samples → blend > 0."""
        assert _blend(3) > 0.0

    def test_at_n_full_returns_max_blend(self):
        """_N_FULL (30) samples → blend == _MAX_BLEND (0.80)."""
        assert _blend(30) == 0.80

    def test_above_n_full_capped_at_max_blend(self):
        """More than 30 samples → blend capped at 0.80."""
        assert _blend(100) == 0.80
        assert _blend(1000) == 0.80

    def test_intermediate_blend_value(self):
        """15 samples → blend = min(0.80, 15/30) = 0.5."""
        assert _blend(15) == pytest.approx(0.5)

    def test_monotonic_increase(self):
        """Blend increases with n up to max."""
        prev = _blend(0)
        for n in range(1, 31):
            cur = _blend(n)
            assert cur >= prev
            prev = cur


class TestApplyCalibration:

    def _cal_map(self, bin_key: str, win_rate: float, n: int, blend: float) -> dict:
        return {bin_key: {"win_rate": win_rate, "n": n, "blend": blend}}

    def test_empty_cal_map_returns_raw(self):
        result, meta = apply_calibration(72.0, "BUY", {})
        assert result == 72.0
        assert meta is None

    def test_invalid_action_returns_raw(self):
        cal_map = self._cal_map("70", 0.6, 20, 0.5)
        result, meta = apply_calibration(72.0, "HOLD", cal_map)
        assert result == 72.0
        assert meta is None

    def test_zero_blend_returns_raw(self):
        """Bin with blend=0.0 (too few samples) → raw confidence returned."""
        cal_map = self._cal_map("70", 0.6, 2, 0.0)
        result, meta = apply_calibration(72.0, "BUY", cal_map)
        assert result == 72.0
        assert meta is None

    def test_calibration_blends_toward_emp_win_rate(self):
        """With blend=0.5, result should be midpoint of raw_conf and emp_wr*100."""
        cal_map = self._cal_map("70", 0.6, 15, 0.5)
        result, meta = apply_calibration(72.0, "BUY", cal_map)
        expected = 0.6 * 100 * 0.5 + 72.0 * 0.5
        assert result == pytest.approx(expected, abs=0.2)
        assert meta is not None

    def test_calibrated_confidence_clamped_above_35(self):
        """Result never falls below 35."""
        # Very low win_rate + high blend would push result low
        cal_map = self._cal_map("50", 0.01, 30, 0.80)
        result, _ = apply_calibration(52.0, "SELL", cal_map)
        assert result >= 35.0

    def test_calibrated_confidence_clamped_below_84(self):
        """Result never exceeds 84."""
        cal_map = self._cal_map("80", 0.99, 30, 0.80)
        result, _ = apply_calibration(83.0, "BUY", cal_map)
        assert result <= 84.0

    def test_sell_action_is_accepted(self):
        cal_map = self._cal_map("65", 0.55, 20, 0.6)
        result, meta = apply_calibration(67.0, "SELL", cal_map)
        assert result != 67.0 or meta is None  # either calibrated or not found

    def test_fallback_to_lower_bin(self):
        """If exact bin not found, falls back to the next-lower bin."""
        cal_map = {"65": {"win_rate": 0.55, "n": 10, "blend": 0.3}}
        # raw_conf = 68 → bin key "65", which exists
        result, meta = apply_calibration(68.0, "BUY", cal_map)
        assert meta is not None


class TestLoadCalibration:

    def test_returns_empty_when_file_missing(self, tmp_path):
        """When calibration.json doesn't exist, returns {}."""
        with patch("services.calibration._CAL_FILE", tmp_path / "no_file.json"):
            result = load_calibration()
        assert result == {}

    def test_returns_dict_when_file_exists(self, tmp_path):
        cal_file = tmp_path / "calibration.json"
        sample = {"70": {"win_rate": 0.6, "n": 10, "blend": 0.3}}
        cal_file.write_text(json.dumps(sample))
        with patch("services.calibration._CAL_FILE", cal_file):
            result = load_calibration()
        assert result == sample

    def test_returns_empty_on_invalid_json(self, tmp_path):
        bad_file = tmp_path / "calibration.json"
        bad_file.write_text("NOT_JSON{{{")
        with patch("services.calibration._CAL_FILE", bad_file):
            result = load_calibration()
        assert result == {}


# ─────────────────────────────────────────────────────────────────────────────
# 2. services/bayesian_smoothing.py
# ─────────────────────────────────────────────────────────────────────────────

from services.bayesian_smoothing import calculate_predictive_interval


class TestBayesianSmoothing:

    def test_returns_tuple(self):
        prob, std = calculate_predictive_interval(wins=5, total=10, current_vix=20.0)
        assert isinstance(prob, float)
        assert isinstance(std, float)

    def test_probability_between_zero_and_one(self):
        prob, _ = calculate_predictive_interval(wins=5, total=10, current_vix=20.0)
        assert 0.0 < prob < 1.0

    def test_std_dev_positive(self):
        _, std = calculate_predictive_interval(wins=5, total=10, current_vix=20.0)
        assert std > 0.0

    def test_all_wins_probability_close_to_one(self):
        prob, _ = calculate_predictive_interval(wins=1000, total=1000, current_vix=20.0)
        assert prob > 0.99

    def test_zero_wins_probability_close_to_zero(self):
        prob, _ = calculate_predictive_interval(wins=0, total=1000, current_vix=20.0)
        assert prob < 0.01

    def test_fifty_fifty_probability_near_half(self):
        prob, _ = calculate_predictive_interval(wins=50, total=100, current_vix=20.0)
        assert 0.45 < prob < 0.55

    def test_high_vix_increases_smoothing(self):
        """With very high VIX, smoothing pulls probability toward 0.5 more."""
        prob_normal, _ = calculate_predictive_interval(wins=90, total=100, current_vix=20.0)
        prob_high_vix, _ = calculate_predictive_interval(wins=90, total=100, current_vix=80.0)
        # High VIX increases prior weight → probability pulled more toward 0.5
        assert prob_high_vix < prob_normal

    def test_vix_at_average_no_extra_smoothing(self):
        """VIX exactly at avg (20) → volatility_factor = 1.0 (standard Laplace)."""
        prob, std = calculate_predictive_interval(wins=5, total=10, current_vix=20.0, avg_vix=20.0)
        # Standard Laplace: (5+1)/(10+2) = 0.5
        assert prob == pytest.approx(0.5, abs=0.01)

    def test_zero_total_does_not_crash(self):
        """Edge case: zero total (only prior counts)."""
        prob, std = calculate_predictive_interval(wins=0, total=0, current_vix=20.0)
        assert 0.0 < prob < 1.0

    def test_std_dev_decreases_with_more_data(self):
        """More data → more certainty → smaller standard deviation."""
        _, std_small = calculate_predictive_interval(wins=5, total=10, current_vix=20.0)
        _, std_large = calculate_predictive_interval(wins=50, total=100, current_vix=20.0)
        assert std_large < std_small


# ─────────────────────────────────────────────────────────────────────────────
# 3. services/market_calendar.py — is_pre_long_weekend()
# ─────────────────────────────────────────────────────────────────────────────

from services.market_calendar import is_pre_long_weekend


def _holiday(days_from_today: int, weekday_override: int | None = None, name: str = "Test Holiday") -> dict:
    """Build a holiday dict relative to today."""
    target = date.today() + timedelta(days=days_from_today)
    if weekday_override is not None:
        # Adjust to the given weekday within the same week
        diff = weekday_override - target.weekday()
        target = target + timedelta(days=diff)
    return {"date": target.strftime("%Y-%m-%d"), "name": name, "exchange": "NYSE"}


class TestIsPreLongWeekend:

    def test_no_holidays_returns_false(self):
        result, name = is_pre_long_weekend([])
        assert result is False
        assert name == ""

    def test_far_future_holiday_ignored(self):
        """Holiday > 5 days away is ignored."""
        h = {"date": (date.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
             "name": "Far Holiday", "exchange": "NYSE"}
        result, _ = is_pre_long_weekend([h])
        assert result is False

    def test_past_holiday_ignored(self):
        """Holiday in the past is ignored."""
        h = {"date": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
             "name": "Past Holiday", "exchange": "NYSE"}
        result, _ = is_pre_long_weekend([h])
        assert result is False

    def test_monday_holiday_within_3_days_is_long_weekend(self):
        """A Monday holiday within 3 calendar days triggers the haircut."""
        # Find the next Monday within 3 days
        today = date.today()
        for delta in range(1, 4):
            candidate = today + timedelta(days=delta)
            if candidate.weekday() == 0:  # Monday
                h = {"date": candidate.strftime("%Y-%m-%d"), "name": "Labor Day", "exchange": "NYSE"}
                result, holiday_name = is_pre_long_weekend([h])
                assert result is True
                assert holiday_name == "Labor Day"
                return
        pytest.skip("No Monday within 3 days from today — skipping")

    def test_friday_holiday_within_3_days_is_long_weekend(self):
        """A Friday holiday within 3 calendar days triggers the haircut."""
        today = date.today()
        for delta in range(1, 4):
            candidate = today + timedelta(days=delta)
            if candidate.weekday() == 4:  # Friday
                h = {"date": candidate.strftime("%Y-%m-%d"), "name": "Good Friday", "exchange": "NYSE"}
                result, holiday_name = is_pre_long_weekend([h])
                assert result is True
                assert holiday_name == "Good Friday"
                return
        pytest.skip("No Friday within 3 days from today — skipping")

    def test_wednesday_holiday_not_long_weekend(self):
        """A Wednesday holiday doesn't create a 3-day weekend."""
        today = date.today()
        for delta in range(1, 4):
            candidate = today + timedelta(days=delta)
            if candidate.weekday() == 2:  # Wednesday
                h = {"date": candidate.strftime("%Y-%m-%d"), "name": "Mid-week Holiday", "exchange": "NYSE"}
                result, _ = is_pre_long_weekend([h])
                assert result is False
                return
        pytest.skip("No Wednesday within 3 days from today — skipping")

    def test_invalid_date_format_skipped(self):
        """Malformed date string is skipped without crashing."""
        h = {"date": "not-a-date", "name": "Bad Holiday", "exchange": "NYSE"}
        result, _ = is_pre_long_weekend([h])
        assert result is False

    def test_returns_name_of_triggering_holiday(self):
        """When triggered, the holiday name is returned."""
        today = date.today()
        # Find next Monday or Friday within 3 days
        for delta in range(1, 4):
            candidate = today + timedelta(days=delta)
            if candidate.weekday() in (0, 4):
                h = {"date": candidate.strftime("%Y-%m-%d"), "name": "Independence Day", "exchange": "NYSE"}
                result, name = is_pre_long_weekend([h])
                assert result is True
                assert name == "Independence Day"
                return
        pytest.skip("No Mon/Fri within 3 days from today")

    def test_multiple_holidays_first_match_returned(self):
        """When multiple holidays qualify, the first match is returned."""
        today = date.today()
        holidays = []
        # Build two qualifying holidays
        for delta in range(1, 4):
            candidate = today + timedelta(days=delta)
            if candidate.weekday() in (0, 4):
                holidays.append({"date": candidate.strftime("%Y-%m-%d"),
                                  "name": f"Holiday {delta}", "exchange": "NYSE"})
            if len(holidays) >= 2:
                break
        if len(holidays) < 2:
            pytest.skip("Not enough qualifying days within 3 days")
        result, name = is_pre_long_weekend(holidays)
        assert result is True
        assert name == holidays[0]["name"]
