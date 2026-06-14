"""Daily per-user signal view quota enforcement.

Tracks how many signals a user has retrieved through `/api/signals` and
`/api/signals/history` in the current UTC day.  Paid tiers that are not in
``active`` status are downgraded to the free quota until billing is resolved.
Owners always bypass quotas.
"""

from datetime import datetime, timezone

from config import get_quota_for_tier
from models import User, UserSignalQuota
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _utc_midnight() -> datetime:
    """Return the start of the current UTC day as a naive datetime.

    The rest of the codebase stores naive UTC timestamps, so we keep the quota
    window consistent with that convention.
    """
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, now.day)


def get_effective_tier(user: User) -> str:
    """Return the tier that should govern quota limits for this user.

    Owners bypass tier checks.  Paid users whose subscription is not active are
    treated as free until billing is resolved.
    """
    if user.is_owner:
        return "pro"  # pro maps to unlimited; owner bypass happens in quota helper
    if user.subscription_tier in ("basic", "pro") and user.subscription_status != "active":
        return "free"
    return user.subscription_tier or "free"


def get_user_quota_limit(user: User) -> int | None:
    """Daily signal view limit for the user, or None if unlimited."""
    return get_quota_for_tier(get_effective_tier(user), is_owner=user.is_owner)


async def get_or_create_quota(db: AsyncSession, user: User) -> UserSignalQuota:
    """Fetch the user's quota row, creating or rolling the daily window if needed."""
    today = _utc_midnight()
    stmt = select(UserSignalQuota).where(UserSignalQuota.user_id == user.id)
    row = (await db.execute(stmt)).scalar_one_or_none()

    if row is None:
        row = UserSignalQuota(user_id=user.id, window_start=today, views_count=0)
        db.add(row)
        # Flush so the row is visible for subsequent reads in the same transaction.
        await db.flush()
    elif row.window_start != today:
        row.window_start = today
        row.views_count = 0

    return row


async def apply_signal_quota(
    db: AsyncSession,
    user: User,
    requested_limit: int,
) -> dict:
    """Compute how many signals the user may view right now.

    Returns a dict with:
        - quota: UserSignalQuota — the quota row (pass to record_signal_views)
        - limit: int | None — tier daily limit (None = unlimited)
        - remaining: int | None — signals left today (None = unlimited)
        - allowed_count: int — how many signals may be returned this request
        - window_start: datetime — UTC midnight of the current quota window
        - exceeded: bool — True when no signals remain
    """
    quota = await get_or_create_quota(db, user)
    limit = get_user_quota_limit(user)

    if limit is None:
        return {
            "quota": quota,
            "limit": None,
            "remaining": None,
            "allowed_count": requested_limit,
            "window_start": quota.window_start,
            "exceeded": False,
        }

    remaining = max(limit - quota.views_count, 0)
    allowed_count = min(remaining, requested_limit)
    return {
        "quota": quota,
        "limit": limit,
        "remaining": remaining,
        "allowed_count": allowed_count,
        "window_start": quota.window_start,
        "exceeded": allowed_count == 0,
    }


async def record_signal_views(db: AsyncSession, quota: UserSignalQuota, count: int) -> None:
    """Increment the consumed signal count."""
    if count <= 0:
        return
    quota.views_count = (quota.views_count or 0) + count
    await db.flush()
