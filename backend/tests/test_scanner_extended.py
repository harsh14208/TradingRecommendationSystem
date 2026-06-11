"""
Extended unit tests for services/scanner.py

Coverage targets:
  _maybe_send:
    - HOLD action → returns immediately (no DB query, no send)
    - confidence below threshold → skipped
    - profit_pct below 2% → skipped
    - outside market hours → suppressed
    - 24h cooldown active → skipped
    - successful BUY send → db_row.is_sent set to True

  _fanout_to_subscribers:
    - no token → returns False immediately
    - no eligible users → returns False
    - owner bypasses subscription check
    - dedup: already-delivered user_id skipped
    - per-user confidence threshold respected
    - duplicate chat_id skipped (sent_chat_ids dedup)
"""

import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr
from services import scanner

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _settings(**kwargs):
    defaults = dict(
        telegram_bot_token=SecretStr("bot:TOKEN"),
        telegram_chat_id="-100123",
        min_confidence=55.0,
        telegram_broadcast_channel_id="",
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _sig(action="BUY", ticker="AAPL", confidence=75.0, price=150.0, entry=148.0, target=155.0, stop=144.0, **extra):
    base = dict(
        action=action,
        ticker=ticker,
        confidence=confidence,
        price=price,
        entry=entry,
        target=target,
        stop=stop,
        headline="Test headline",
        rr="2.5",
        # Both swing and position now require ≥2 non-TA sources (§33 live data:
        # swing alpha −1.028%/trade; single non-TA source insufficient).
        sources=["Technical", "Macro", "Options"],
        rationale=[],
        hasMr=True,  # MR gate required for BUY delivery (2026-06-02 fix)
    )
    base.update(extra)
    return base


def _db_row(**kwargs):
    row = MagicMock()
    row.id = 99
    row.is_sent = False
    row.sent_at = None
    row.created_at = None
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


def _make_db(sent_signal=None):
    """Return an async session mock.

    sent_signal: if provided, scalar_one_or_none() returns it (cooldown hit).
    """
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sent_signal
    # For scalars().all() used in cooldown loss-streak query
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock.scalars.return_value = scalars_mock

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result_mock)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


# ---------------------------------------------------------------------------
# _maybe_send tests
# ---------------------------------------------------------------------------


class TestMaybeSend:
    @pytest.mark.asyncio
    async def test_hold_action_skipped_immediately(self):
        """HOLD signals must never trigger a send path."""
        db = _make_db()
        row = _db_row()
        settings = _settings()

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))) as mock_send:
                with patch.object(scanner, "_fanout_to_subscribers", new=AsyncMock(return_value=(False, None))):
                    await scanner._maybe_send(_sig(action="HOLD"), row, settings, db, "test")
                mock_send.assert_not_called()

        assert row.is_sent is False

    @pytest.mark.asyncio
    async def test_confidence_below_threshold_skipped(self):
        db = _make_db()
        row = _db_row()
        settings = _settings(min_confidence=80.0)

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))) as mock_send:
                await scanner._maybe_send(_sig(confidence=60.0), row, settings, db, "test")
            mock_send.assert_not_called()

        assert row.is_sent is False

    @pytest.mark.asyncio
    async def test_profit_pct_below_2_percent_skipped(self):
        """entry=100, target=101 → profit_pct=1% < 2% → skip."""
        db = _make_db()
        row = _db_row()
        settings = _settings(min_confidence=55.0)

        sig = _sig(entry=100.0, target=101.0, stop=98.0, confidence=70.0)

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch("services.market_calendar.get_upcoming_holidays", new=AsyncMock(return_value=[])):
                with patch("services.market_calendar.is_pre_long_weekend", return_value=(False, "")):
                    with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))) as mock_send:
                        await scanner._maybe_send(sig, row, settings, db, "test")
                    mock_send.assert_not_called()

        assert row.is_sent is False

    @pytest.mark.asyncio
    async def test_outside_market_hours_suppressed(self):
        db = _make_db()
        row = _db_row()
        settings = _settings()

        with patch.object(scanner, "_market_hours_ok", return_value=False):
            with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))) as mock_send:
                await scanner._maybe_send(_sig(confidence=70.0), row, settings, db, "test")
            mock_send.assert_not_called()

        assert row.is_sent is False

    @pytest.mark.asyncio
    async def test_24h_cooldown_active_skipped(self):
        """Cooldown: DB returns an existing sent Signal → skip."""
        existing_sent = MagicMock()  # non-None means cooldown hit

        cooldown_result = MagicMock()
        cooldown_result.scalar_one_or_none.return_value = existing_sent

        # loss-streak query returns empty list
        streak_result = MagicMock()
        streak_scalars = MagicMock()
        streak_scalars.all.return_value = []
        streak_result.scalars.return_value = streak_scalars

        db = AsyncMock()
        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return streak_result  # loss-streak query
            return cooldown_result  # cooldown query

        db.execute = _execute
        db.add = MagicMock()

        row = _db_row()
        settings = _settings()

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))) as mock_send:
                with patch.object(scanner, "_fanout_to_subscribers", new=AsyncMock(return_value=(False, None))):
                    with patch("services.market_calendar.get_upcoming_holidays", new=AsyncMock(return_value=[])):
                        with patch("services.market_calendar.is_pre_long_weekend", return_value=(False, "")):
                            await scanner._maybe_send(_sig(confidence=70.0), row, settings, db, "test")
                mock_send.assert_not_called()

        assert row.is_sent is False

    @pytest.mark.asyncio
    async def test_successful_buy_send_marks_row_as_sent(self):
        """Happy-path: no cooldown, market hours OK → is_sent=True.
        DB query order (post-refactor):
          1. daily-cap check        → scalar_one_or_none=None (no send today)
          2. sector concentration   → scalar_one()=0 (if sector is set)
          3. loss-streak check      → scalars().all()=[]
          4. 24h cooldown           → scalar_one_or_none=None
        """
        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        no_result.scalar_one.return_value = 0

        streak_result = MagicMock()
        streak_scalars = MagicMock()
        streak_scalars.all.return_value = []
        streak_result.scalars.return_value = streak_scalars
        streak_result.scalar_one_or_none.return_value = None
        streak_result.scalar_one.return_value = 0

        db = AsyncMock()
        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            # Call 1: daily-cap OR sector concentration → no previous send
            # Call 2: loss-streak → empty list
            # Call 3+: cooldown → no previous send
            if call_count[0] == 2:
                return streak_result
            return no_result

        db.execute = _execute
        db.add = MagicMock()

        row = _db_row()
        settings = _settings()

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch.object(scanner, "_fanout_to_subscribers", new=AsyncMock(return_value=(True, "12345"))):
                with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "99"))):
                    with patch("services.market_calendar.get_upcoming_holidays", new=AsyncMock(return_value=[])):
                        with patch("services.market_calendar.is_pre_long_weekend", return_value=(False, "")):
                            with patch("asyncio.create_task"):
                                with patch("asyncio.ensure_future"):
                                    await scanner._maybe_send(_sig(confidence=70.0), row, settings, db, "new")

        assert row.is_sent is True

    @pytest.mark.asyncio
    async def test_send_log_added_after_successful_send(self):
        """A SendLog row must be added to the session on success."""
        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        no_result.scalar_one.return_value = 0

        streak_result = MagicMock()
        streak_scalars = MagicMock()
        streak_scalars.all.return_value = []
        streak_result.scalars.return_value = streak_scalars
        streak_result.scalar_one_or_none.return_value = None
        streak_result.scalar_one.return_value = 0

        db = AsyncMock()
        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            if call_count[0] == 2:
                return streak_result
            return no_result

        db.execute = _execute
        added_objects = []
        db.add = lambda obj: added_objects.append(obj)

        row = _db_row()
        settings = _settings()

        from models import SendLog

        with patch.object(scanner, "_market_hours_ok", return_value=True):
            with patch.object(scanner, "_fanout_to_subscribers", new=AsyncMock(return_value=(True, "12345"))):
                with patch.object(scanner, "send_telegram", new=AsyncMock(return_value=(True, "1"))):
                    with patch("services.market_calendar.get_upcoming_holidays", new=AsyncMock(return_value=[])):
                        with patch("services.market_calendar.is_pre_long_weekend", return_value=(False, "")):
                            with patch("asyncio.create_task"):
                                with patch("asyncio.ensure_future"):
                                    await scanner._maybe_send(_sig(), row, settings, db, "new")

        # At least one SendLog object should have been added
        assert any(isinstance(o, SendLog) for o in added_objects)


# ---------------------------------------------------------------------------
# _fanout_to_subscribers tests
# ---------------------------------------------------------------------------


class TestFanoutToSubscribers:
    @pytest.mark.asyncio
    async def test_no_token_returns_false_immediately(self):
        settings_no_token = types.SimpleNamespace(telegram_bot_token=SecretStr(""))

        db = AsyncMock()
        row = _db_row()

        with patch("services.scanner.get_settings", return_value=settings_no_token):
            result = await scanner._fanout_to_subscribers(_sig(), row, db)

        assert result == (False, None)
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_eligible_users_returns_false(self):
        settings_ok = types.SimpleNamespace(
            telegram_bot_token=SecretStr("bot:TOKEN"),
            min_confidence=55.0,
        )

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []  # zero subscribers
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock

        db = AsyncMock()
        db.execute = AsyncMock(return_value=result_mock)
        db.flush = AsyncMock()

        row = _db_row()

        with patch("services.scanner.get_settings", return_value=settings_ok):
            result = await scanner._fanout_to_subscribers(_sig(), row, db)

        assert result == (False, None)

    @pytest.mark.asyncio
    async def test_owner_bypasses_subscription_tier_check(self):
        settings_ok = types.SimpleNamespace(
            telegram_bot_token=SecretStr("bot:TOKEN"),
            min_confidence=55.0,
        )

        owner = MagicMock()
        owner.id = 1
        owner.is_owner = True
        owner.subscription_status = "inactive"
        owner.subscription_tier = "free"
        owner.telegram_chat_id = "OWNER_CHAT"
        owner.min_confidence_override = None

        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                # subscribers query
                scalars = MagicMock()
                scalars.all.return_value = [owner]
                result.scalars.return_value = scalars
            elif call_count[0] == 2:
                # delivered_user_ids query
                delivered_scalars = MagicMock()
                delivered_scalars.all.return_value = []
                result.scalars.return_value = delivered_scalars
            return result

        db = AsyncMock()
        db.execute = _execute
        db.add = MagicMock()
        db.flush = AsyncMock()

        row = _db_row(id=10)

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 5}})

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("services.scanner.get_settings", return_value=settings_ok):
            with patch("services.scanner.format_signal", return_value="msg"):
                with patch("aiohttp.ClientSession", return_value=mock_ctx):
                    with patch("services.scanner.asyncio.create_task"):
                        result = await scanner._fanout_to_subscribers(_sig(), row, db)

        assert result == (True, "OWNER_CHAT")

    @pytest.mark.asyncio
    async def test_dedup_skips_already_delivered_user(self):
        settings_ok = types.SimpleNamespace(
            telegram_bot_token=SecretStr("bot:TOKEN"),
            min_confidence=55.0,
        )

        user = MagicMock()
        user.id = 7
        user.is_owner = False
        user.subscription_status = "active"
        user.subscription_tier = "basic"
        user.telegram_chat_id = "CHAT7"
        user.min_confidence_override = None

        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                scalars = MagicMock()
                scalars.all.return_value = [user]
                result.scalars.return_value = scalars
            elif call_count[0] == 2:
                # user.id=7 already in delivered list → dedup should skip
                delivered_scalars = MagicMock()
                delivered_scalars.all.return_value = [7]
                result.scalars.return_value = delivered_scalars
            return result

        db = AsyncMock()
        db.execute = _execute
        db.add = MagicMock()
        db.flush = AsyncMock()

        row = _db_row(id=10)

        mock_session = AsyncMock()
        mock_session.post = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("services.scanner.get_settings", return_value=settings_ok):
            with patch("services.scanner.format_signal", return_value="msg"):
                with patch("aiohttp.ClientSession", return_value=mock_ctx):
                    with patch("services.scanner.asyncio.create_task"):
                        result = await scanner._fanout_to_subscribers(_sig(), row, db)

        # No post should have been called because user was already delivered
        mock_session.post.assert_not_called()
        assert result == (False, None)

    @pytest.mark.asyncio
    async def test_per_user_confidence_threshold_blocks_low_conf_signal(self):
        settings_ok = types.SimpleNamespace(
            telegram_bot_token=SecretStr("bot:TOKEN"),
            min_confidence=55.0,
        )

        user = MagicMock()
        user.id = 3
        user.is_owner = False
        user.subscription_status = "active"
        user.subscription_tier = "basic"
        user.telegram_chat_id = "CHAT3"
        user.min_confidence_override = 90.0  # very high personal threshold

        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                scalars = MagicMock()
                scalars.all.return_value = [user]
                result.scalars.return_value = scalars
            elif call_count[0] == 2:
                delivered_scalars = MagicMock()
                delivered_scalars.all.return_value = []
                result.scalars.return_value = delivered_scalars
            return result

        db = AsyncMock()
        db.execute = _execute
        db.add = MagicMock()
        db.flush = AsyncMock()

        row = _db_row(id=10)

        mock_session = AsyncMock()
        mock_session.post = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("services.scanner.get_settings", return_value=settings_ok):
            with patch("services.scanner.format_signal", return_value="msg"):
                with patch("aiohttp.ClientSession", return_value=mock_ctx):
                    with patch("services.scanner.asyncio.create_task"):
                        # Signal confidence = 70, user threshold = 90 → blocked
                        result = await scanner._fanout_to_subscribers(_sig(confidence=70.0), row, db)

        mock_session.post.assert_not_called()
        assert result == (False, None)

    @pytest.mark.asyncio
    async def test_duplicate_chat_id_sent_only_once(self):
        """Two users sharing the same telegram_chat_id: only the first gets a message."""
        settings_ok = types.SimpleNamespace(
            telegram_bot_token=SecretStr("bot:TOKEN"),
            min_confidence=55.0,
        )

        def _make_eligible_user(uid, chat_id):
            u = MagicMock()
            u.id = uid
            u.is_owner = False
            u.subscription_status = "active"
            u.subscription_tier = "basic"
            u.telegram_chat_id = chat_id
            u.min_confidence_override = None
            u.discord_webhook_url = None  # isolate the telegram chat-dedup path
            return u

        user_a = _make_eligible_user(1, "SHARED_CHAT")
        user_b = _make_eligible_user(2, "SHARED_CHAT")  # same chat_id

        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                scalars = MagicMock()
                scalars.all.return_value = [user_a, user_b]
                result.scalars.return_value = scalars
            else:
                delivered_scalars = MagicMock()
                delivered_scalars.all.return_value = []
                result.scalars.return_value = delivered_scalars
            return result

        db = AsyncMock()
        db.execute = _execute
        db.add = MagicMock()
        db.flush = AsyncMock()

        row = _db_row(id=10)

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value={"ok": True, "result": {"message_id": 11}})
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_queue = AsyncMock()
        with patch("services.scanner.get_settings", return_value=settings_ok):
            with patch("services.scanner.format_signal", return_value="msg"):
                with patch("services.delivery_manager.queue_delivery", mock_queue):
                    with patch("services.scanner.asyncio.create_task"):
                        result = await scanner._fanout_to_subscribers(_sig(), row, db)

        # Delivery should be queued exactly once despite two eligible users sharing a chat
        assert mock_queue.call_count == 1
        assert result == (True, "SHARED_CHAT")

    @pytest.mark.asyncio
    async def test_notification_prefs_enforced(self):
        """PROD-3: a user who saved telegram=False receives no fanout delivery."""
        settings_ok = types.SimpleNamespace(telegram_bot_token=SecretStr("bot:TOKEN"), min_confidence=55.0)

        user = MagicMock()
        user.id = 1
        user.is_owner = False
        user.subscription_status = "active"
        user.subscription_tier = "basic"
        user.telegram_chat_id = "CHAT_1"
        user.min_confidence_override = None

        # AppSettings row whose data disables telegram for user 1.
        app_row = MagicMock()
        app_row.data = {"user_1_notification_prefs": {"telegram": False}}

        call_count = [0]

        async def _execute(_stmt):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:  # eligible users
                result.scalars.return_value.all.return_value = [user]
            elif call_count[0] == 4:  # AppSettings (users → delivered → SignalAlert → AppSettings)
                result.scalar_one_or_none.return_value = app_row
            else:  # delivered + ticker rules
                result.scalars.return_value.all.return_value = []
            return result

        db = AsyncMock()
        db.execute = _execute
        db.add = MagicMock()
        db.flush = AsyncMock()

        mock_session = AsyncMock()
        mock_session.post = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("services.scanner.get_settings", return_value=settings_ok):
            with patch("services.scanner.format_signal", return_value="msg"):
                with patch("aiohttp.ClientSession", return_value=mock_ctx):
                    with patch("services.scanner.asyncio.create_task"):
                        result = await scanner._fanout_to_subscribers(_sig(), _db_row(id=10), db)

        assert mock_session.post.call_count == 0
        assert result == (False, None)
