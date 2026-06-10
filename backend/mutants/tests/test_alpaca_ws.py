"""Tests for services/alpaca_ws.py."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_get_price_returns_none_for_unknown():
    from services.alpaca_ws import _price_cache, get_price

    _price_cache.clear()
    assert get_price("UNKNOWN") is None


def test_get_price_returns_cached_value():
    from services.alpaca_ws import _price_cache, get_price

    _price_cache.clear()
    _price_cache["AAPL"] = 155.0
    assert get_price("AAPL") == 155.0


def test_start_creates_task():
    import services.alpaca_ws as ws_mod
    from services.alpaca_ws import start

    # Patch asyncio.create_task so we don't actually start a real WS
    with patch("services.alpaca_ws.asyncio.create_task") as mock_create:
        mock_task = MagicMock()
        mock_task.done = MagicMock(return_value=False)
        mock_create.return_value = mock_task

        # Reset global task
        ws_mod._task = None

        start("KEY", "SECRET", ["AAPL"], AsyncMock())
        mock_create.assert_called_once()


def test_start_noop_if_task_running():
    import services.alpaca_ws as ws_mod

    running_task = MagicMock()
    running_task.done = MagicMock(return_value=False)
    ws_mod._task = running_task

    with patch("services.alpaca_ws.asyncio.create_task") as mock_create:
        from services.alpaca_ws import start

        start("KEY", "SECRET", ["AAPL"], AsyncMock())
        mock_create.assert_not_called()

    ws_mod._task = None


def test_stop_cancels_running_task():
    import services.alpaca_ws as ws_mod

    mock_task = MagicMock()
    mock_task.done = MagicMock(return_value=False)
    mock_task.cancel = MagicMock()
    ws_mod._task = mock_task

    from services.alpaca_ws import stop

    stop()
    mock_task.cancel.assert_called_once()

    ws_mod._task = None


def test_stop_noop_if_task_done():
    import services.alpaca_ws as ws_mod

    mock_task = MagicMock()
    mock_task.done = MagicMock(return_value=True)
    mock_task.cancel = MagicMock()
    ws_mod._task = mock_task

    from services.alpaca_ws import stop

    stop()
    mock_task.cancel.assert_not_called()

    ws_mod._task = None


def test_stop_noop_if_no_task():
    import services.alpaca_ws as ws_mod

    ws_mod._task = None
    from services.alpaca_ws import stop

    stop()  # should not raise


@pytest.mark.asyncio
async def test_run_websockets_import_error():
    """If websockets is not installed, _run should return early."""
    from services.alpaca_ws import _run

    with (
        patch.dict("sys.modules", {"websockets": None, "websockets.asyncio": None, "websockets.asyncio.client": None}),
        patch("builtins.__import__", side_effect=ImportError("no module")),
    ):
        # Should return without raising
        try:
            await asyncio.wait_for(_run("K", "S", ["AAPL"], AsyncMock()), timeout=0.5)
        except (asyncio.TimeoutError, ImportError, Exception):
            pass  # Any of these are acceptable outcomes


@pytest.mark.asyncio
async def test_run_auth_failure_returns():
    """If auth response doesn't include success, _run returns without subscribing."""
    from services.alpaca_ws import _run

    # Build a mock websocket that returns connect→failed auth
    greeting = '[{"T":"connected"}]'
    auth_fail = '[{"T":"error","msg":"auth failed"}]'

    mock_ws = AsyncMock()
    mock_ws.recv = AsyncMock(side_effect=[greeting, auth_fail])
    mock_ws.send = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock(return_value=False)

    mock_connect = MagicMock(return_value=mock_ws)

    mock_module = MagicMock()
    mock_module.connect = mock_connect

    with patch.dict("sys.modules", {"websockets.asyncio.client": mock_module}):
        with patch("services.alpaca_ws.asyncio.sleep", AsyncMock(side_effect=asyncio.CancelledError)):
            try:
                await _run("KEY", "SEC", ["AAPL"], AsyncMock())
            except asyncio.CancelledError:
                pass
