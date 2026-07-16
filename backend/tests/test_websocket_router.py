"""Tests for WebSocket signal broadcast eligibility."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models import User
from routers.websocket_router import ConnectionManager, _user_can_receive_signals


@pytest.fixture
def manager():
    m = ConnectionManager()
    yield m
    m._connections.clear()


def _make_ws():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


def _make_user(tier="free", status="inactive", owner=False, active=True):
    return User(
        id=1,
        email="u@t.com",
        subscription_tier=tier,
        subscription_status=status,
        is_owner=owner,
        is_active=active,
    )


class TestUserCanReceiveSignals:
    def test_owner(self):
        assert _user_can_receive_signals(_make_user(owner=True)) is True

    def test_active_basic(self):
        assert _user_can_receive_signals(_make_user("basic", "active")) is True

    def test_active_pro(self):
        assert _user_can_receive_signals(_make_user("pro", "active")) is True

    def test_free_user(self):
        assert _user_can_receive_signals(_make_user("free", "inactive")) is False

    def test_inactive_paid(self):
        assert _user_can_receive_signals(_make_user("basic", "canceled")) is False

    def test_inactive_user(self):
        assert _user_can_receive_signals(_make_user("pro", "active", active=False)) is False

    def test_none_user(self):
        assert _user_can_receive_signals(None) is False


@pytest.mark.asyncio
class TestConnectionManager:
    async def test_connect_adds_eligible_flag(self, manager):
        ws = _make_ws()
        await manager.connect(ws, _make_user("pro", "active"))
        assert len(manager._connections) == 1
        assert manager._connections[0].eligible_for_signals is True

    async def test_connect_adds_ineligible_flag(self, manager):
        ws = _make_ws()
        await manager.connect(ws, _make_user("free", "inactive"))
        assert manager._connections[0].eligible_for_signals is False

    async def test_broadcast_signal_sends_only_to_eligible(self, manager):
        eligible_ws = _make_ws()
        ineligible_ws = _make_ws()
        await manager.connect(eligible_ws, _make_user("pro", "active"))
        await manager.connect(ineligible_ws, _make_user("free", "inactive"))

        await manager.broadcast_signal({"type": "new_signal", "signal": {"id": 1}})

        eligible_ws.send_text.assert_awaited_once()
        ineligible_ws.send_text.assert_not_awaited()

    async def test_broadcast_non_signal_sends_to_all(self, manager):
        eligible_ws = _make_ws()
        ineligible_ws = _make_ws()
        await manager.connect(eligible_ws, _make_user("pro", "active"))
        await manager.connect(ineligible_ws, _make_user("free", "inactive"))

        await manager.broadcast({"type": "price_update", "quotes": []})

        eligible_ws.send_text.assert_awaited_once()
        ineligible_ws.send_text.assert_awaited_once()

    async def test_disconnect_removes_connection(self, manager):
        ws = _make_ws()
        await manager.connect(ws, _make_user("pro", "active"))
        await manager.disconnect(ws)
        assert len(manager._connections) == 0
