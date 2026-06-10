"""Tests for services/stop_monitor.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── _fetch_current_prices ─────────────────────────────────────────────────────


def test_fetch_prices_empty_tickers():
    from services.stop_monitor import _fetch_current_prices

    assert _fetch_current_prices([]) == {}


def test_fetch_prices_multi_ticker_dataframe():
    import pandas as pd
    from services.stop_monitor import _fetch_current_prices

    close_data = pd.DataFrame({"Close": {"AAPL": 150.0, "GOOG": 100.0}})
    # Simulate multi-ticker: close.iloc[-1] has .items()
    mock_data = MagicMock()
    mock_data.columns = ["Close"]
    close_df = MagicMock()
    last_row = MagicMock()
    last_row.items = MagicMock(return_value=[("AAPL", 150.0), ("GOOG", 100.0)])
    close_df.iloc.__getitem__ = MagicMock(return_value=last_row)
    mock_data.__contains__ = lambda self, item: item == "Close"
    mock_data.__getitem__ = MagicMock(return_value=close_df)

    with patch("services.stop_monitor.yf.download", return_value=mock_data):
        result = _fetch_current_prices(["AAPL", "GOOG"])

    assert result == {"AAPL": 150.0, "GOOG": 100.0}


def test_fetch_prices_single_ticker_scalar():
    from services.stop_monitor import _fetch_current_prices

    mock_data = MagicMock()
    mock_data.columns = ["Close"]
    close_df = MagicMock()
    last_row = 155.0
    close_df.iloc.__getitem__ = MagicMock(return_value=last_row)
    mock_data.__contains__ = lambda self, item: item == "Close"
    mock_data.__getitem__ = MagicMock(return_value=close_df)

    with patch("services.stop_monitor.yf.download", return_value=mock_data):
        result = _fetch_current_prices(["AAPL"])

    assert result == {"AAPL": 155.0}


def test_fetch_prices_no_close_column():
    from services.stop_monitor import _fetch_current_prices

    mock_data = MagicMock()
    mock_data.columns = ["Open"]
    mock_data.__contains__ = lambda self, item: item != "Close"

    with patch("services.stop_monitor.yf.download", return_value=mock_data):
        result = _fetch_current_prices(["AAPL"])

    assert result == {}


def test_fetch_prices_nan_skipped():
    from services.stop_monitor import _fetch_current_prices

    mock_data = MagicMock()
    mock_data.columns = ["Close"]
    close_df = MagicMock()
    last_row = MagicMock()
    last_row.items = MagicMock(return_value=[("AAPL", float("nan")), ("GOOG", 100.0)])
    close_df.iloc.__getitem__ = MagicMock(return_value=last_row)
    mock_data.__contains__ = lambda self, item: item == "Close"
    mock_data.__getitem__ = MagicMock(return_value=close_df)

    with patch("services.stop_monitor.yf.download", return_value=mock_data):
        result = _fetch_current_prices(["AAPL", "GOOG"])

    assert "AAPL" not in result
    assert result["GOOG"] == 100.0


def test_fetch_prices_exception_returns_empty():
    from services.stop_monitor import _fetch_current_prices

    with patch("services.stop_monitor.yf.download", side_effect=Exception("network error")):
        result = _fetch_current_prices(["AAPL"])

    assert result == {}


# ── _send_stop_target_notification ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_notification_calls_telegram():
    from services.stop_monitor import _send_stop_target_notification

    mock_settings = MagicMock()
    mock_settings.telegram_chat_id = "chat123"

    with (
        patch("config.get_settings", return_value=mock_settings),
        patch("services.telegram_svc.send_telegram_message", AsyncMock(return_value=(True, "1"))) as mock_tg,
        patch("services.market_data.COMPANY_NAMES", {"AAPL": "Apple Inc"}),
    ):
        await _send_stop_target_notification("AAPL", "BUY", "target", 155.0, 150.0, 2.5, 42)

    mock_tg.assert_awaited_once()
    call_args = mock_tg.call_args[0]
    assert "chat123" in call_args


@pytest.mark.asyncio
async def test_send_notification_stop_event():
    from services.stop_monitor import _send_stop_target_notification

    mock_settings = MagicMock()
    mock_settings.telegram_chat_id = "chat999"

    with (
        patch("config.get_settings", return_value=mock_settings),
        patch("services.telegram_svc.send_telegram_message", AsyncMock(return_value=(True, "1"))) as mock_tg,
        patch("services.market_data.COMPANY_NAMES", {}),
    ):
        await _send_stop_target_notification("TSLA", "BUY", "stop", 95.0, 97.0, -3.0, 7)

    msg_text = mock_tg.call_args[0][1]
    assert "STOP HIT" in msg_text


@pytest.mark.asyncio
async def test_send_notification_exception_suppressed():
    from services.stop_monitor import _send_stop_target_notification

    with (
        patch("config.get_settings", side_effect=Exception("config error")),
    ):
        await _send_stop_target_notification("AAPL", "BUY", "target", 155.0, 150.0, 2.5, 1)
        # Should not raise


# ── check_stop_targets_and_notify ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_active_signals_exits_early():
    from services.stop_monitor import check_stop_targets_and_notify

    mock_db_ctx = AsyncMock()
    mock_db_ctx.__aenter__ = AsyncMock(return_value=mock_db_ctx)
    mock_db_ctx.__aexit__ = AsyncMock(return_value=False)

    scalars = MagicMock()
    scalars.all = MagicMock(return_value=[])
    result = MagicMock()
    result.scalars = MagicMock(return_value=scalars)
    mock_db_ctx.execute = AsyncMock(return_value=result)

    with patch("database.AsyncSessionLocal", return_value=mock_db_ctx):
        await check_stop_targets_and_notify()


def _make_signal(id=1, ticker="AAPL", action="BUY", entry=100.0, stop=95.0, target=110.0):
    sig = MagicMock()
    sig.id = id
    sig.ticker = ticker
    sig.action = action
    sig.entry = entry
    sig.stop = stop
    sig.target = target
    sig.hit_stop = False
    sig.hit_target = False
    sig.exit_type = None
    sig.is_active = True
    sig.outcome_pct = None
    return sig


@pytest.mark.asyncio
async def test_buy_signal_hits_target():
    from services.stop_monitor import check_stop_targets_and_notify

    sig = _make_signal(ticker="AAPL", action="BUY", entry=100.0, stop=95.0, target=110.0)
    sig_db = _make_signal(ticker="AAPL", action="BUY", entry=100.0, stop=95.0, target=110.0)

    call_count = 0

    def _make_ctx():
        nonlocal call_count
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.commit = AsyncMock()

        if call_count == 0:
            # First DB session: return active signals
            scalars = MagicMock()
            scalars.all = MagicMock(return_value=[sig])
            result = MagicMock()
            result.scalars = MagicMock(return_value=scalars)
            ctx.execute = AsyncMock(return_value=result)
        else:
            # Second DB session: signal lookup by ID
            scalar_result = MagicMock()
            scalar_result.scalar_one_or_none = MagicMock(return_value=sig_db)
            ctx.execute = AsyncMock(return_value=scalar_result)

        call_count += 1
        return ctx

    with (
        patch("database.AsyncSessionLocal", side_effect=_make_ctx),
        patch("services.stop_monitor._fetch_current_prices", return_value={"AAPL": 115.0}),
        patch("services.stop_monitor.asyncio.create_task"),
    ):
        await check_stop_targets_and_notify()

    assert sig_db.hit_target is True
    assert sig_db.exit_type == "target"
    assert sig_db.is_active is False
    # outcome_pct uses the target price (110), not the current price (115)
    assert sig_db.outcome_pct == pytest.approx(10.0, rel=0.01)


@pytest.mark.asyncio
async def test_buy_signal_hits_stop():
    from services.stop_monitor import check_stop_targets_and_notify

    sig = _make_signal(ticker="TSLA", action="BUY", entry=200.0, stop=190.0, target=220.0)
    sig_db = _make_signal(ticker="TSLA", action="BUY", entry=200.0, stop=190.0, target=220.0)

    call_count = 0

    def _make_ctx():
        nonlocal call_count
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.commit = AsyncMock()

        if call_count == 0:
            scalars = MagicMock()
            scalars.all = MagicMock(return_value=[sig])
            result = MagicMock()
            result.scalars = MagicMock(return_value=scalars)
            ctx.execute = AsyncMock(return_value=result)
        else:
            scalar_result = MagicMock()
            scalar_result.scalar_one_or_none = MagicMock(return_value=sig_db)
            ctx.execute = AsyncMock(return_value=scalar_result)

        call_count += 1
        return ctx

    with (
        patch("database.AsyncSessionLocal", side_effect=_make_ctx),
        patch("services.stop_monitor._fetch_current_prices", return_value={"TSLA": 185.0}),
        patch("services.stop_monitor.asyncio.create_task"),
    ):
        await check_stop_targets_and_notify()

    assert sig_db.hit_stop is True
    assert sig_db.exit_type == "stop"
    assert sig_db.outcome_pct < 0


@pytest.mark.asyncio
async def test_no_price_for_ticker_skipped():
    from services.stop_monitor import check_stop_targets_and_notify

    sig = _make_signal(ticker="NOPRICE")

    call_count = 0

    def _make_ctx():
        nonlocal call_count
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.commit = AsyncMock()

        if call_count == 0:
            scalars = MagicMock()
            scalars.all = MagicMock(return_value=[sig])
            result = MagicMock()
            result.scalars = MagicMock(return_value=scalars)
            ctx.execute = AsyncMock(return_value=result)

        call_count += 1
        return ctx

    with (
        patch("database.AsyncSessionLocal", side_effect=_make_ctx),
        patch("services.stop_monitor._fetch_current_prices", return_value={}),
    ):
        await check_stop_targets_and_notify()

    assert sig.exit_type is None


@pytest.mark.asyncio
async def test_signal_not_found_in_second_db_session_skipped():
    from services.stop_monitor import check_stop_targets_and_notify

    sig = _make_signal(ticker="AAPL", action="BUY", entry=100.0, stop=95.0, target=110.0)

    call_count = 0

    def _make_ctx():
        nonlocal call_count
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.commit = AsyncMock()

        if call_count == 0:
            scalars = MagicMock()
            scalars.all = MagicMock(return_value=[sig])
            result = MagicMock()
            result.scalars = MagicMock(return_value=scalars)
            ctx.execute = AsyncMock(return_value=result)
        else:
            scalar_result = MagicMock()
            scalar_result.scalar_one_or_none = MagicMock(return_value=None)
            ctx.execute = AsyncMock(return_value=scalar_result)

        call_count += 1
        return ctx

    with (
        patch("database.AsyncSessionLocal", side_effect=_make_ctx),
        patch("services.stop_monitor._fetch_current_prices", return_value={"AAPL": 115.0}),
    ):
        await check_stop_targets_and_notify()


@pytest.mark.asyncio
async def test_sell_signal_stop_and_target_inverted():
    from services.stop_monitor import check_stop_targets_and_notify

    # SELL: stop is above entry, target is below entry
    sig = _make_signal(ticker="AAPL", action="SELL", entry=100.0, stop=105.0, target=90.0)
    sig_db = _make_signal(ticker="AAPL", action="SELL", entry=100.0, stop=105.0, target=90.0)

    call_count = 0

    def _make_ctx():
        nonlocal call_count
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.commit = AsyncMock()

        if call_count == 0:
            scalars = MagicMock()
            scalars.all = MagicMock(return_value=[sig])
            result = MagicMock()
            result.scalars = MagicMock(return_value=scalars)
            ctx.execute = AsyncMock(return_value=result)
        else:
            scalar_result = MagicMock()
            scalar_result.scalar_one_or_none = MagicMock(return_value=sig_db)
            ctx.execute = AsyncMock(return_value=scalar_result)

        call_count += 1
        return ctx

    # Price hits target (drops to 88)
    with (
        patch("database.AsyncSessionLocal", side_effect=_make_ctx),
        patch("services.stop_monitor._fetch_current_prices", return_value={"AAPL": 88.0}),
        patch("services.stop_monitor.asyncio.create_task"),
    ):
        await check_stop_targets_and_notify()

    assert sig_db.hit_target is True
    assert sig_db.exit_type == "target"
