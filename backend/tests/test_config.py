"""
Tests for config.py — Settings properties, tier helpers, and get_settings().
All tests are pure and rely only on the in-process Settings object.
"""

import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from config import (
    TIER_LABELS,
    TIER_PLAN_FEATURES,
    TIER_PRICES_CENTS,
    TIERS,
    Settings,
    get_settings,
    has_feature,
    tier_gte,
)

# ── Settings.tickers property ──────────────────────────────────────────────────


class TestSettingsTickers:
    def test_default_watchlist_returns_list(self):
        s = Settings()
        tickers = s.tickers
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_tickers_are_uppercase(self):
        s = Settings(watchlist="aapl,tsla,nvda")
        assert s.tickers == ["AAPL", "TSLA", "NVDA"]

    def test_strips_whitespace(self):
        s = Settings(watchlist=" AAPL , TSLA ")
        assert s.tickers == ["AAPL", "TSLA"]

    def test_empty_watchlist_returns_empty(self):
        s = Settings(watchlist="")
        assert s.tickers == []

    def test_single_ticker(self):
        s = Settings(watchlist="SPY")
        assert s.tickers == ["SPY"]


# ── Settings.jwt_secret_key property ──────────────────────────────────────────


class TestJwtSecretKey:
    def test_returns_set_secret(self):
        s = Settings(jwt_secret="MY_VERY_SECRET_KEY_THAT_IS_LONG_ENOUGH_32")
        assert s.jwt_secret_key == "MY_VERY_SECRET_KEY_THAT_IS_LONG_ENOUGH_32"

    def test_falls_back_to_dev_secret_when_empty(self):
        s = Settings(jwt_secret="")
        # Dev secret is a non-empty random string
        assert len(s.jwt_secret_key) > 0
        assert s.jwt_secret_key != ""


# ── has_feature ────────────────────────────────────────────────────────────────


class TestHasFeature:
    def test_owner_has_all_features(self):
        """Owner bypasses tier checks — always returns True."""
        assert has_feature("free", "paper_trading", is_owner=True) is True
        assert has_feature("free", "anything_at_all", is_owner=True) is True

    def test_free_tier_has_signals_view(self):
        assert has_feature("free", "signals_view") is True

    def test_free_tier_lacks_telegram(self):
        assert has_feature("free", "telegram") is False

    def test_basic_tier_has_telegram(self):
        assert has_feature("basic", "telegram") is True

    def test_basic_tier_lacks_paper_trading(self):
        assert has_feature("basic", "paper_trading") is False

    def test_pro_tier_has_all_basic_plus_paper_trading(self):
        assert has_feature("pro", "paper_trading") is True

    def test_unknown_feature_returns_false(self):
        assert has_feature("pro", "nonexistent_feature") is False

    def test_unknown_tier_returns_false(self):
        assert has_feature("enterprise", "signals_view") is False


# ── tier_gte ───────────────────────────────────────────────────────────────────


class TestTierGte:
    def test_same_tier_is_gte(self):
        assert tier_gte("free", "free") is True
        assert tier_gte("basic", "basic") is True
        assert tier_gte("pro", "pro") is True

    def test_higher_tier_gte_lower(self):
        assert tier_gte("basic", "free") is True
        assert tier_gte("pro", "free") is True
        assert tier_gte("pro", "basic") is True

    def test_lower_tier_not_gte_higher(self):
        assert tier_gte("free", "basic") is False
        assert tier_gte("free", "pro") is False
        assert tier_gte("basic", "pro") is False


# ── TIERS constant ─────────────────────────────────────────────────────────────


class TestTiersConstant:
    def test_tiers_is_list(self):
        assert isinstance(TIERS, list)

    def test_tiers_contains_expected_values(self):
        assert "free" in TIERS
        assert "basic" in TIERS
        assert "pro" in TIERS

    def test_tiers_order_free_first(self):
        assert TIERS[0] == "free"

    def test_tiers_order_pro_last(self):
        assert TIERS[-1] == "pro"

    def test_paid_plan_prices_are_current_public_prices(self):
        assert TIER_PRICES_CENTS["basic"] == 2900
        assert TIER_PRICES_CENTS["pro"] == 7900
        assert "$29/mo" in TIER_LABELS["basic"]
        assert "$79/mo" in TIER_LABELS["pro"]

    def test_plan_features_match_tiers(self):
        assert set(TIER_PLAN_FEATURES) == set(TIERS)
        assert "Telegram signal delivery" in TIER_PLAN_FEATURES["basic"]
        assert "Paper trading (Alpaca)" in TIER_PLAN_FEATURES["pro"]


# ── get_settings ───────────────────────────────────────────────────────────────


class TestGetSettings:
    def test_returns_settings_instance(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_returns_same_instance_twice(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_min_confidence_has_default(self):
        s = get_settings()
        assert isinstance(s.min_confidence, float)
        assert 0 < s.min_confidence <= 100
