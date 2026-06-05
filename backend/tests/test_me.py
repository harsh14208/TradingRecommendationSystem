"""
Tests for routers/me.py — /api/me/performance endpoint.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_user(user_id=1, **kwargs):
    u = MagicMock()
    u.id = user_id
    u.is_owner = False
    u.subscription_tier = "pro"
    u.subscription_status = "active"
    for k, v in kwargs.items():
        setattr(u, k, v)
    return u


def _make_signal(
    id=1,
    ticker="AAPL",
    action="BUY",
    confidence=72.0,
    price=180.0,
    outcome_pct=None,
    hit_target=None,
    hit_stop=None,
    exit_type=None,
    mae=None,
    mfe=None,
    outcome_14d=None,
):
    s = MagicMock()
    s.id = id
    s.ticker = ticker
    s.company = ticker
    s.action = action
    s.confidence = confidence
    s.price = price
    s.style = "swing"
    s.created_at = None
    s.outcome_pct = outcome_pct
    s.outcome_14d = outcome_14d
    s.hit_target = hit_target
    s.hit_stop = hit_stop
    s.exit_type = exit_type
    s.mae = mae
    s.mfe = mfe
    return s


# ── _sig_row helper ───────────────────────────────────────────────────────────


def test_sig_row_resolved():
    from routers.me import _sig_row

    sig = _make_signal(outcome_pct=2.5, hit_target=True, exit_type="target")
    row = _sig_row(sig, None)
    assert row["ticker"] == "AAPL"
    assert row["outcome_pct"] == 2.5
    assert row["hit_target"] is True
    assert row["exit_type"] == "target"


def test_sig_row_open():
    from routers.me import _sig_row

    sig = _make_signal(outcome_pct=None)
    row = _sig_row(sig, None)
    assert row["outcome_pct"] is None


def test_sig_row_rounds_outcome():
    from routers.me import _sig_row

    sig = _make_signal(outcome_pct=1.23456)
    row = _sig_row(sig, None)
    assert row["outcome_pct"] == 1.23


# ── /api/me/performance stats computation ────────────────────────────────────


@pytest.mark.asyncio
async def test_performance_no_signals():
    from routers.me import my_performance

    user = _make_user()
    db = AsyncMock()

    # No deliveries at all
    db.execute = AsyncMock(
        return_value=MagicMock(
            all=MagicMock(return_value=[]), scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        )
    )

    result = await my_performance(limit=50, user=user, db=db)
    assert result["stats"]["delivered"] == 0
    assert result["stats"]["resolved"] == 0
    assert result["stats"]["win_rate"] is None
    assert result["stats"]["avg_return"] is None
    assert result["recent"] == []


@pytest.mark.asyncio
async def test_performance_with_resolved_signals():
    from datetime import datetime

    from routers.me import my_performance

    user = _make_user()
    db = AsyncMock()

    sent_ts = datetime(2026, 1, 15)
    sig1 = _make_signal(id=1, outcome_pct=3.0)
    sig2 = _make_signal(id=2, outcome_pct=-1.0)
    sig3 = _make_signal(id=3, outcome_pct=None)  # open

    call_count = 0

    async def fake_execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            # First call: JOIN query returning (signal, sent_at) pairs
            result.all = MagicMock(return_value=[(sig1, sent_ts), (sig2, sent_ts), (sig3, sent_ts)])
        else:
            # Second call: COUNT query
            result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[1, 2, 3])))
        return result

    db.execute = fake_execute

    result = await my_performance(limit=50, user=user, db=db)
    stats = result["stats"]

    assert stats["delivered"] == 3
    assert stats["resolved"] == 2
    assert stats["wins"] == 1
    assert stats["losses"] == 1
    assert stats["win_rate"] == 50.0
    assert stats["avg_return"] == round((3.0 + (-1.0)) / 2, 2)  # 1.0
    assert len(result["recent"]) == 3


@pytest.mark.asyncio
async def test_performance_all_wins():
    from datetime import datetime

    from routers.me import my_performance

    user = _make_user()
    db = AsyncMock()

    sent_ts = datetime(2026, 1, 15)
    signals = [_make_signal(id=i, outcome_pct=float(i + 1)) for i in range(5)]

    call_count = 0

    async def fake_execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            result.all = MagicMock(return_value=[(s, sent_ts) for s in signals])
        else:
            result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=list(range(5)))))
        return result

    db.execute = fake_execute

    result = await my_performance(limit=50, user=user, db=db)
    assert result["stats"]["win_rate"] == 100.0
    assert result["stats"]["losses"] == 0
    # Sharpe computed with ≥5 returns
    assert result["stats"]["sharpe"] is not None


# ── VAL-4: Notification preferences (PROD-3) ─────────────────────────────────


class TestNotificationPrefs:
    """PROD-3: GET/PUT /api/me/notification-prefs — per-user preference roundtrip."""

    @pytest.mark.asyncio
    async def test_get_prefs_returns_defaults_when_no_stored(self):
        from routers.me import get_notification_prefs
        from unittest.mock import AsyncMock, MagicMock

        user = _make_user(user_id=42)
        db = MagicMock()
        # AppSettings row with empty data
        row = MagicMock()
        row.data = {}
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=row)))

        result = await get_notification_prefs(user=user, db=db)
        assert result["telegram"] is True
        assert result["push"] is True
        assert result["min_conf"] == 45.0
        assert result["sectors"] == []

    @pytest.mark.asyncio
    async def test_get_prefs_returns_defaults_when_no_row(self):
        from routers.me import get_notification_prefs

        user = _make_user(user_id=99)
        db = MagicMock()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

        result = await get_notification_prefs(user=user, db=db)
        assert result["telegram"] is True
        assert "min_conf" in result

    @pytest.mark.asyncio
    async def test_put_prefs_merges_partial_update(self):
        from routers.me import NotificationPrefsIn, update_notification_prefs

        user = _make_user(user_id=42)
        db = MagicMock()
        row = MagicMock()
        row.data = {}
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=row)))
        db.commit = AsyncMock()

        body = NotificationPrefsIn(min_conf=47.5, sectors=["XLK"], email=False)
        result = await update_notification_prefs(body=body, user=user, db=db)
        assert result["min_conf"] == 47.5
        assert "XLK" in result["sectors"]
        assert result["email"] is False
        # Unset fields keep defaults
        assert result["telegram"] is True

    @pytest.mark.asyncio
    async def test_put_prefs_user_isolation(self):
        """Two different users should have independent preference keys."""
        from routers.me import _user_pref_key

        assert _user_pref_key(1) != _user_pref_key(2)
        assert "1" in _user_pref_key(1)
        assert "2" in _user_pref_key(2)
