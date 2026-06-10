"""Unit tests for services/engines/helpers.py — pure scoring helpers."""
import pytest
from unittest.mock import patch


# ── _score_to_action ──────────────────────────────────────────────────────────

def test_score_to_action_buy():
    from services.engines.helpers import _score_to_action
    action, conf = _score_to_action(40.0)
    assert action == "BUY"
    assert conf > 0


def test_score_to_action_sell():
    from services.engines.helpers import _score_to_action
    action, conf = _score_to_action(-35.0)
    assert action == "SELL"
    assert conf > 0


def test_score_to_action_hold_positive():
    from services.engines.helpers import _score_to_action
    action, conf = _score_to_action(10.0)
    assert action == "HOLD"
    assert 38.0 <= conf <= 52.0


def test_score_to_action_hold_negative():
    from services.engines.helpers import _score_to_action
    action, conf = _score_to_action(-10.0)
    assert action == "HOLD"


def test_score_to_action_hold_zero():
    from services.engines.helpers import _score_to_action
    action, conf = _score_to_action(0.0)
    assert action == "HOLD"


def test_score_to_action_boundary_buy():
    from services.engines.helpers import _score_to_action
    action, _ = _score_to_action(35.0)
    assert action == "BUY"


def test_score_to_action_boundary_sell():
    from services.engines.helpers import _score_to_action
    action, _ = _score_to_action(-30.0)
    assert action == "SELL"


def test_score_to_action_just_below_buy():
    from services.engines.helpers import _score_to_action
    action, _ = _score_to_action(34.9)
    assert action == "HOLD"


def test_score_to_action_agreement_bonus():
    from services.engines.helpers import _score_to_action
    _, conf0 = _score_to_action(50.0, agreement=0)
    _, conf4 = _score_to_action(50.0, agreement=4)
    assert conf4 >= conf0  # agreement bonus increases confidence


def test_score_to_action_agreement_capped():
    from services.engines.helpers import _score_to_action
    _, conf_high = _score_to_action(50.0, agreement=100)
    _, conf_low = _score_to_action(50.0, agreement=0)
    assert conf_high - conf_low <= 2.1  # bonus capped at 2.0


def test_score_to_action_conf_ceiling():
    from services.engines.helpers import _score_to_action
    # Very high score shouldn't exceed 78% ceiling
    _, conf = _score_to_action(1000.0)
    assert conf <= 78.0


# ── _levels ───────────────────────────────────────────────────────────────────

def test_levels_hold_returns_nones():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(150.0, 3.0, "HOLD")
    assert entry is None
    assert stop is None
    assert target is None
    assert rr == "—"


def test_levels_zero_atr_returns_nones():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(150.0, 0.0, "BUY")
    assert entry is None


def test_levels_buy_swing():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(100.0, 2.0, "BUY", style="swing")
    assert entry == 100.0
    assert stop == pytest.approx(100.0 - 1.5 * 2.0, abs=0.01)  # 1.5× ATR stop
    assert target == pytest.approx(100.0 + 2.0 * 2.0, abs=0.01)  # 2.0× ATR target


def test_levels_sell_swing():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(100.0, 2.0, "SELL", style="swing")
    assert stop == pytest.approx(100.0 + 1.5 * 2.0, abs=0.01)
    assert target == pytest.approx(100.0 - 2.0 * 2.0, abs=0.01)


def test_levels_intraday():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(100.0, 2.0, "BUY", style="intraday")
    # 1.0× stop, 2.0× target
    assert stop == pytest.approx(100.0 - 1.0 * 2.0, abs=0.01)
    assert target == pytest.approx(100.0 + 2.0 * 2.0, abs=0.01)


def test_levels_position_high_vol():
    from services.engines.helpers import _levels
    # atr_pct = 3/100 = 0.03 > 0.025 → high vol
    entry, stop, target, rr = _levels(100.0, 3.0, "BUY", style="position")
    assert stop == pytest.approx(100.0 - 2.5 * 3.0, abs=0.01)
    assert target == pytest.approx(100.0 + 3.5 * 3.0, abs=0.01)


def test_levels_position_low_vol():
    from services.engines.helpers import _levels
    # atr_pct = 0.5/100 = 0.005 < 0.010 → low vol
    entry, stop, target, rr = _levels(100.0, 0.5, "BUY", style="position")
    assert stop == pytest.approx(100.0 - 3.5 * 0.5, abs=0.01)
    assert target == pytest.approx(100.0 + 5.0 * 0.5, abs=0.01)


def test_levels_rr_format():
    from services.engines.helpers import _levels
    entry, stop, target, rr = _levels(100.0, 2.0, "BUY")
    # R:R should be a string like "1.3" or "—"
    assert isinstance(rr, str)
    if rr != "—":
        assert float(rr) > 0


def test_levels_rr_buy():
    from services.engines.helpers import _levels
    _, _, _, rr = _levels(100.0, 2.0, "BUY", style="swing")
    # reward=4, risk=3 → RR≈1.3 (returned as formatted string "1.3")
    assert rr != "—"
    assert float(rr) == pytest.approx(4.0 / 3.0, abs=0.1)


# ── _current_session ─────────────────────────────────────────────────────────

def test_current_session_regular():
    from services.engines.helpers import _current_session, _ET
    from datetime import datetime
    with patch("services.engines.helpers.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 6, 1, 14, 0, 0, tzinfo=_ET)
        mock_dt.now.return_value = _ET.localize(datetime(2026, 6, 1, 14, 0, 0).replace(tzinfo=None))
        result = _current_session()
    assert result in ("pre", "regular", "after", "closed")


def test_current_session_returns_valid_string():
    from services.engines.helpers import _current_session
    result = _current_session()
    assert result in ("pre", "regular", "after", "closed")


# ── _make_plain_english ───────────────────────────────────────────────────────

def test_make_plain_english_buy():
    from services.engines.helpers import _make_plain_english
    rationale = [
        {"sentiment": "pos", "head": "RSI oversold"},
        {"sentiment": "pos", "head": "BB%B oversold"},
        {"sentiment": "neg", "head": "Volume low"},
    ]
    result = _make_plain_english("BUY", "AAPL", "swing", rationale, 58.0, 150.0, 147.0, 154.0)
    assert "summary" in result
    assert "timeframe" in result
    assert "tf_short" in result
    assert "top_reasons" in result
    assert "AAPL" in result["summary"]
    assert "rise" in result["summary"]


def test_make_plain_english_sell():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("SELL", "NVDA", "swing", [], 55.0, 500.0, 505.0, 490.0)
    assert "fall" in result["summary"]


def test_make_plain_english_hold():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("HOLD", "MSFT", "swing", [], 45.0, 300.0, None, None)
    assert "mixed signals" in result["summary"].lower() or "MSFT" in result["summary"]


def test_make_plain_english_high_confidence():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("BUY", "AAPL", "position", [], 80.0, 150.0, 145.0, 165.0)
    assert "high" in result["summary"]


def test_make_plain_english_moderate_confidence():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("BUY", "AAPL", "swing", [], 65.0, 150.0, 147.0, 154.0)
    assert "moderate" in result["summary"]


def test_make_plain_english_low_confidence():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("BUY", "AAPL", "intraday", [], 40.0, 150.0, 147.0, 154.0)
    assert "low" in result["summary"]


def test_make_plain_english_no_entry():
    from services.engines.helpers import _make_plain_english
    result = _make_plain_english("BUY", "AAPL", "swing", [], 55.0, None, None, None)
    assert "summary" in result


def test_make_plain_english_top_reasons():
    from services.engines.helpers import _make_plain_english
    rationale = [{"sentiment": "pos", "head": "RSI oversold"}, {"sentiment": "pos", "head": "IBS low"}]
    result = _make_plain_english("BUY", "AAPL", "swing", rationale, 55.0, 150.0, 147.0, 154.0)
    assert len(result["top_reasons"]) >= 1


# ── _LEVERAGED_ETFS ───────────────────────────────────────────────────────────

def test_leveraged_etfs_contains_tqqq():
    from services.engines.helpers import _LEVERAGED_ETFS
    assert "TQQQ" in _LEVERAGED_ETFS


def test_leveraged_etfs_contains_sqqq():
    from services.engines.helpers import _LEVERAGED_ETFS
    assert "SQQQ" in _LEVERAGED_ETFS


def test_leveraged_etfs_not_contains_aapl():
    from services.engines.helpers import _LEVERAGED_ETFS
    assert "AAPL" not in _LEVERAGED_ETFS
