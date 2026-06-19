"""Alpaca options-order broker implementation.

Uses Alpaca's unified ``POST /v2/orders`` endpoint for both single-leg and
multi-leg option orders.  Multi-leg orders set ``order_class: "mleg"`` with a
``legs`` array; single-leg orders send the OCC symbol directly.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from services.brokers.options_broker import OptionLeg, OptionOrder, OptionsBroker
from services.http_client import shared_session

log = logging.getLogger("signal.brokers.alpaca_options")

_PAPER_BASE = "https://paper-api.alpaca.markets"
_LIVE_BASE = "https://api.alpaca.markets"


def _base_url(paper: bool) -> str:
    return _PAPER_BASE if paper else _LIVE_BASE


def _headers(api_key: str, api_secret: str) -> dict[str, str]:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }


def _position_intent(leg: OptionLeg, opening: bool = True) -> str:
    """Map our side/position to Alpaca's position_intent enum value."""
    if opening:
        if leg.side == "buy":
            return "buy_to_open"
        return "sell_to_open"
    if leg.side == "buy":
        return "buy_to_close"
    return "sell_to_close"


class AlpacaOptionsBroker(OptionsBroker):
    name = "alpaca"

    def __init__(self, api_key: str, api_secret: str, paper: bool = True) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = _base_url(paper)

    async def place_option_order(self, order: OptionOrder) -> dict[str, Any]:
        """Submit an option order to Alpaca and return a normalized status dict."""
        if not order.legs:
            return {"status": "rejected", "reason": "no legs in option order"}

        client_order_id = f"sig-opt-{uuid.uuid4().hex[:12]}"
        body: dict[str, Any] = {
            "type": "market",
            "time_in_force": "day",
            "client_order_id": client_order_id,
        }

        if len(order.legs) == 1:
            leg = order.legs[0]
            body.update(
                {
                    "symbol": leg.option_symbol.upper(),
                    "qty": str(int(leg.quantity)),
                    "side": leg.side,
                    "position_intent": _position_intent(leg, opening=True),
                }
            )
        else:
            body["order_class"] = "mleg"
            body["qty"] = str(sum(int(leg.quantity) for leg in order.legs))
            body["legs"] = [
                {
                    "side": leg.side,
                    "position_intent": _position_intent(leg, opening=True),
                    "symbol": leg.option_symbol.upper(),
                    "ratio_qty": str(int(leg.quantity)),
                }
                for leg in order.legs
            ]

        url = f"{self.base_url}/v2/orders"
        try:
            async with shared_session() as session:
                async with session.post(
                    url,
                    headers=_headers(self.api_key, self.api_secret),
                    json=body,
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except Exception as exc:
            log.warning("Alpaca options order failed for %s: %s", order.underlying, exc)
            return {
                "status": "error",
                "reason": str(exc)[:500],
                "client_order_id": client_order_id,
            }

        return {
            "status": data.get("status", "submitted"),
            "alpaca_order_id": data.get("id"),
            "client_order_id": client_order_id,
            "raw": data,
        }

    async def close_option_position(self, option_symbol: str, qty: int | None = None) -> dict[str, Any]:
        """Close an open option position by option symbol.

        If ``qty`` is omitted the entire position is liquidated.
        """
        url = f"{self.base_url}/v2/positions/{option_symbol.upper()}"
        params: dict[str, str] = {}
        if qty is not None and qty > 0:
            params["qty"] = str(int(qty))

        try:
            async with shared_session() as session:
                async with session.delete(
                    url,
                    headers=_headers(self.api_key, self.api_secret),
                    params=params,
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except Exception as exc:
            log.warning("Alpaca options close failed for %s: %s", option_symbol, exc)
            return {"status": "error", "reason": str(exc)[:500]}

        return {"status": "closed", "raw": data}

    async def get_option_position(self, option_symbol: str) -> dict[str, Any] | None:
        """Return the current position for an option symbol, or None if flat."""
        url = f"{self.base_url}/v2/positions/{option_symbol.upper()}"
        try:
            async with shared_session() as session:
                async with session.get(url, headers=_headers(self.api_key, self.api_secret)) as resp:
                    if resp.status == 404:
                        return None
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as exc:
            log.warning("Alpaca options position lookup failed for %s: %s", option_symbol, exc)
            return None
