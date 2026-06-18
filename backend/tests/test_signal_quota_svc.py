"""Unit tests for services.signal_quota_svc."""

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from config import SIGNAL_QUOTAS, get_quota_for_tier
from models import User, UserSignalQuota
from services.signal_quota_svc import (
    _utc_midnight,
    apply_signal_quota,
    get_effective_tier,
    get_or_create_quota,
    get_user_quota_limit,
    record_signal_views,
)


def _make_user(tier="free", status="inactive", is_owner=False):
    return User(
        id=1,
        email="test@example.com",
        subscription_tier=tier,
        subscription_status=status,
        is_owner=is_owner,
    )


class TestTierAndQuotaHelpers:
    def test_get_effective_tier_free(self):
        assert get_effective_tier(_make_user("free", "inactive")) == "free"

    def test_get_effective_tier_active_basic(self):
        assert get_effective_tier(_make_user("basic", "active")) == "basic"

    def test_get_effective_tier_inactive_basic_downgrades(self):
        assert get_effective_tier(_make_user("basic", "past_due")) == "free"

    def test_get_effective_tier_owner(self):
        assert get_effective_tier(_make_user("free", "inactive", is_owner=True)) == "pro"

    def test_get_quota_for_tier_owner_unlimited(self):
        assert get_quota_for_tier("free", is_owner=True) is None

    def test_get_quota_for_tier_matches_config(self):
        assert get_quota_for_tier("free") == SIGNAL_QUOTAS["free"]
        assert get_quota_for_tier("basic") == SIGNAL_QUOTAS["basic"]
        assert get_quota_for_tier("pro") is None

    def test_get_quota_for_tier_unknown_defaults_to_free(self):
        assert get_quota_for_tier("enterprise") == SIGNAL_QUOTAS["free"]

    def test_get_user_quota_limit(self):
        assert get_user_quota_limit(_make_user("free")) == 3
        assert get_user_quota_limit(_make_user("basic", "active")) == 100
        assert get_user_quota_limit(_make_user("pro", "active")) is None
        assert get_user_quota_limit(_make_user("elite", "active")) is None
        assert get_user_quota_limit(_make_user("pro", "past_due")) == 3  # downgraded
        assert get_user_quota_limit(_make_user("free", is_owner=True)) is None


class TestUtcMidnight:
    def test_returns_start_of_utc_day(self):
        midnight = _utc_midnight()
        now = datetime.now(timezone.utc)
        assert midnight.year == now.year
        assert midnight.month == now.month
        assert midnight.day == now.day
        assert midnight.hour == midnight.minute == midnight.second == 0
        assert midnight.tzinfo is None


@pytest.mark.asyncio
class TestGetOrCreateQuota:
    async def test_creates_row_when_missing(self):
        db = MagicMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        db.flush = AsyncMock()

        user = _make_user()
        quota = await get_or_create_quota(db, user)

        assert quota.user_id == 1
        assert quota.views_count == 0
        assert quota.window_start == _utc_midnight()
        db.add.assert_called_once_with(quota)
        db.flush.assert_awaited_once()

    async def test_resets_window_when_stale(self):
        yesterday = _utc_midnight() - timedelta(days=1)
        existing = UserSignalQuota(user_id=1, window_start=yesterday, views_count=99)

        db = MagicMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))
        db.flush = AsyncMock()

        quota = await get_or_create_quota(db, _make_user())
        assert quota.window_start == _utc_midnight()
        assert quota.views_count == 0
        db.flush.assert_not_awaited()

    async def test_keeps_todays_count(self):
        today = _utc_midnight()
        existing = UserSignalQuota(user_id=1, window_start=today, views_count=3)

        db = MagicMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))
        db.flush = AsyncMock()

        quota = await get_or_create_quota(db, _make_user())
        assert quota.window_start == today
        assert quota.views_count == 3
        db.flush.assert_not_awaited()


@pytest.mark.asyncio
class TestApplySignalQuota:
    async def test_unlimited_user(self):
        db = MagicMock()
        today = _utc_midnight()
        existing = UserSignalQuota(user_id=1, window_start=today, views_count=0)
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))

        result = await apply_signal_quota(db, _make_user("pro", "active"), 300)
        assert result["limit"] is None
        assert result["remaining"] is None
        assert result["allowed_count"] == 300
        assert result["exceeded"] is False

    async def test_limited_user_with_remaining(self):
        db = MagicMock()
        today = _utc_midnight()
        existing = UserSignalQuota(user_id=1, window_start=today, views_count=2)
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))

        result = await apply_signal_quota(db, _make_user("free"), 300)
        assert result["limit"] == 3
        assert result["remaining"] == 1
        assert result["allowed_count"] == 1
        assert result["exceeded"] is False

    async def test_limited_user_exceeded(self):
        db = MagicMock()
        today = _utc_midnight()
        existing = UserSignalQuota(user_id=1, window_start=today, views_count=3)
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))

        result = await apply_signal_quota(db, _make_user("free"), 300)
        assert result["limit"] == 3
        assert result["remaining"] == 0
        assert result["allowed_count"] == 0
        assert result["exceeded"] is True

    async def test_requested_limit_capped_by_remaining(self):
        db = MagicMock()
        today = _utc_midnight()
        existing = UserSignalQuota(user_id=1, window_start=today, views_count=0)
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))

        result = await apply_signal_quota(db, _make_user("free"), 10)
        assert result["allowed_count"] == 3  # free tier limit is 3


@pytest.mark.asyncio
class TestRecordSignalViews:
    async def test_increments_count(self):
        quota = UserSignalQuota(user_id=1, window_start=_utc_midnight(), views_count=2)
        db = MagicMock()
        db.flush = AsyncMock()

        await record_signal_views(db, quota, 3)
        assert quota.views_count == 5
        db.flush.assert_awaited_once()

    async def test_zero_count_is_noop(self):
        quota = UserSignalQuota(user_id=1, window_start=_utc_midnight(), views_count=2)
        db = MagicMock()
        db.flush = AsyncMock()

        await record_signal_views(db, quota, 0)
        assert quota.views_count == 2
        db.flush.assert_not_awaited()
