"""Tests for services/brokers/alpaca_options.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.brokers.alpaca_options import AlpacaOptionsBroker
from services.brokers.options_broker import OptionLeg, OptionOrder


def _mock_session(json_return=None, status=200):
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
    return session, cm


@pytest.mark.asyncio
async def test_place_single_leg_option_order() -> None:
    session, cm = _mock_session(json_return={"id": "order-1", "status": "accepted"})
    order = OptionOrder(
        underlying="AAPL",
        strategy="SELL_CASH_SEC_PUT",
        legs=[
            OptionLeg(
                side="sell",
                position="short",
                option_symbol="O:AAPL260717P00170000",
                quantity=1,
                strike=170.0,
                expiry="2026-07-17",
            )
        ],
        max_loss=1000.0,
        expected_gain=50.0,
    )
    with patch("services.http_client.get_session", return_value=session):
        broker = AlpacaOptionsBroker("KEY", "SECRET", paper=True)
        result = await broker.place_option_order(order)

    assert result["status"] == "accepted"
    assert result["alpaca_order_id"] == "order-1"
    call_args = session.post.call_args
    assert call_args[0][0] == "https://paper-api.alpaca.markets/v2/orders"
    body = call_args.kwargs["json"]
    assert body["symbol"] == "O:AAPL260717P00170000"
    assert body["side"] == "sell"
    assert body["position_intent"] == "sell_to_open"
    assert body["qty"] == "1"
    assert "legs" not in body


@pytest.mark.asyncio
async def test_place_multi_leg_option_order() -> None:
    session, cm = _mock_session(json_return={"id": "order-2", "status": "accepted"})
    order = OptionOrder(
        underlying="AAPL",
        strategy="LONG_STRADDLE",
        legs=[
            OptionLeg(
                side="buy",
                position="long",
                option_symbol="O:AAPL260717C00170000",
                quantity=1,
                strike=170.0,
                expiry="2026-07-17",
            ),
            OptionLeg(
                side="buy",
                position="long",
                option_symbol="O:AAPL260717P00170000",
                quantity=1,
                strike=170.0,
                expiry="2026-07-17",
            ),
        ],
        max_loss=1000.0,
        expected_gain=50.0,
    )
    with patch("services.http_client.get_session", return_value=session):
        broker = AlpacaOptionsBroker("KEY", "SECRET", paper=True)
        result = await broker.place_option_order(order)

    assert result["status"] == "accepted"
    body = session.post.call_args.kwargs["json"]
    assert body["order_class"] == "mleg"
    assert body["qty"] == "2"
    assert len(body["legs"]) == 2
    assert body["legs"][0]["symbol"] == "O:AAPL260717C00170000"
    assert body["legs"][0]["position_intent"] == "buy_to_open"


@pytest.mark.asyncio
async def test_close_option_position() -> None:
    session, cm = _mock_session(json_return={"status": "queued"})
    with patch("services.http_client.get_session", return_value=session):
        broker = AlpacaOptionsBroker("KEY", "SECRET", paper=True)
        result = await broker.close_option_position("O:AAPL260717C00170000", qty=1)

    assert result["status"] == "closed"
    call_args = session.delete.call_args
    assert call_args[0][0] == "https://paper-api.alpaca.markets/v2/positions/O:AAPL260717C00170000"
    assert call_args.kwargs["params"] == {"qty": "1"}


@pytest.mark.asyncio
async def test_get_option_position_returns_none_on_404() -> None:
    resp = AsyncMock()
    resp.status = 404
    resp.raise_for_status = MagicMock()
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get = MagicMock(return_value=cm)

    with patch("services.http_client.get_session", return_value=session):
        broker = AlpacaOptionsBroker("KEY", "SECRET", paper=True)
        result = await broker.get_option_position("O:AAPL260717C00170000")

    assert result is None
