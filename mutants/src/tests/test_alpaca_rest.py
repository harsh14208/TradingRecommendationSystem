"""Tests for services/alpaca_rest.py."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────


def _mock_session(json_return=None, status=200):
    """Build a minimal aiohttp.ClientSession mock that returns json_return."""
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_return or {})
    resp.raise_for_status = MagicMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=cm)
    session.post = MagicMock(return_value=cm)
    session.delete = MagicMock(return_value=cm)
    return session


# ── _headers / _ssl_ctx ───────────────────────────────────────────────────────


def test_headers_contains_keys():
    from services.alpaca_rest import _headers

    h = _headers("KEY", "SECRET")
    assert h["APCA-API-KEY-ID"] == "KEY"
    assert h["APCA-API-SECRET-KEY"] == "SECRET"
    assert "Content-Type" in h


def test_ssl_ctx_returns_context():
    import ssl
    from services.alpaca_rest import _ssl_ctx

    ctx = _ssl_ctx()
    assert isinstance(ctx, ssl.SSLContext)


# ── get_account ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_account():
    from services.alpaca_rest import get_account

    expected = {"buying_power": "10000"}
    session = _mock_session(json_return=expected)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await get_account("KEY", "SECRET")
    assert result == expected


# ── get_positions ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_positions():
    from services.alpaca_rest import get_positions

    expected = [{"symbol": "AAPL", "qty": "10"}]
    session = _mock_session(json_return=expected)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await get_positions("KEY", "SECRET")
    assert result == expected


# ── get_orders ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_orders():
    from services.alpaca_rest import get_orders

    expected = [{"id": "abc", "symbol": "TSLA"}]
    session = _mock_session(json_return=expected)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await get_orders("KEY", "SECRET", status="open")
    assert result == expected


# ── record_price / check_slippage ─────────────────────────────────────────────


def test_record_price_stores_tick():
    from services.alpaca_rest import _price_history, record_price

    _price_history.clear()
    record_price("AAPL", 150.0)
    assert "AAPL" in _price_history
    assert _price_history["AAPL"][-1][1] == 150.0


def test_record_price_prunes_old_ticks():
    from services.alpaca_rest import _price_history, record_price

    _price_history.clear()
    _price_history["TSLA"] = [(time.time() * 1000 - 5000, 100.0)]  # 5s old
    record_price("TSLA", 105.0)
    # Old tick should be pruned (> 1s old)
    assert all(t > time.time() * 1000 - 1500 for t, _ in _price_history["TSLA"])


def test_check_slippage_no_history_allows():
    from services.alpaca_rest import _price_history, check_slippage

    _price_history.clear()
    should_block, price = check_slippage("UNKNOWN", 100.0)
    assert should_block is False
    assert price is None


def test_check_slippage_within_threshold_allows():
    from services.alpaca_rest import _price_history, check_slippage, record_price

    _price_history.clear()
    record_price("AAPL", 100.02)  # Only $0.02 move
    should_block, price = check_slippage("AAPL", 100.0)
    assert should_block is False


def test_check_slippage_exceeds_threshold_blocks():
    from services.alpaca_rest import _price_history, check_slippage, record_price

    _price_history.clear()
    record_price("AAPL", 100.10)  # $0.10 move > $0.05 threshold
    should_block, price = check_slippage("AAPL", 100.0)
    assert should_block is True
    assert price == pytest.approx(100.10)


def test_check_slippage_empty_window_uses_last():
    from services.alpaca_rest import _price_history, check_slippage

    _price_history.clear()
    # Add a tick that's outside the 100ms window
    old_ts = time.time() * 1000 - 500  # 500ms ago
    _price_history["MSFT"] = [(old_ts, 200.0)]
    should_block, price = check_slippage("MSFT", 199.9)
    assert price == 200.0


# ── place_order ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_place_order_no_slippage():
    from services.alpaca_rest import _price_history, place_order

    _price_history.clear()
    expected = {"id": "order123", "status": "accepted"}
    session = _mock_session(json_return=expected)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await place_order("KEY", "SEC", "AAPL", 10, "buy")
    assert result == expected


@pytest.mark.asyncio
async def test_place_order_slippage_blocked():
    from services.alpaca_rest import _price_history, place_order, record_price

    _price_history.clear()
    record_price("AAPL", 100.10)  # Excessive slippage
    result = await place_order("KEY", "SEC", "AAPL", 10, "buy", signal_price=100.0)
    assert result["rejected"] is True
    assert result["reason"] == "slippage"


@pytest.mark.asyncio
async def test_place_order_limit_type():
    from services.alpaca_rest import _price_history, place_order

    _price_history.clear()
    expected = {"id": "limit_order"}
    session = _mock_session(json_return=expected)
    with patch("aiohttp.ClientSession", return_value=session):
        result = await place_order("KEY", "SEC", "TSLA", 5, "buy", order_type="limit", limit_price=150.0)
    assert result == expected


# ── close_position ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_close_position_204():
    from services.alpaca_rest import close_position

    resp = AsyncMock()
    resp.status = 204
    resp.raise_for_status = MagicMock()
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.delete = MagicMock(return_value=cm)

    with patch("aiohttp.ClientSession", return_value=session):
        result = await close_position("KEY", "SEC", "AAPL")

    assert result == {"status": "closed"}


@pytest.mark.asyncio
async def test_close_position_json_response():
    from services.alpaca_rest import close_position

    expected = {"status": "done"}
    session = _mock_session(json_return=expected, status=200)
    session.delete = session.get  # reuse mock

    with patch("aiohttp.ClientSession", return_value=session):
        result = await close_position("KEY", "SEC", "AAPL")

    assert result == expected


# ── cancel_order ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cancel_order_204():
    from services.alpaca_rest import cancel_order

    resp = AsyncMock()
    resp.status = 204
    resp.raise_for_status = MagicMock()
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.delete = MagicMock(return_value=cm)

    with patch("aiohttp.ClientSession", return_value=session):
        result = await cancel_order("KEY", "SEC", "order-xyz")

    assert result == {"status": "cancelled"}
