"""Alpaca options-order broker implementation.

Alpaca's options API uses OCC symbols and multi-leg order support.  This module
is a stub: the interface is wired, but live order submission is intentionally
left unimplemented until paper-mode validation is complete and options account
approval is confirmed.
"""

from __future__ import annotations

from typing import Any

from services.brokers.options_broker import OptionOrder, OptionsBroker


class AlpacaOptionsBroker(OptionsBroker):
    name = "alpaca"

    def __init__(self, api_key: str, api_secret: str, paper: bool = True) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"

    async def place_option_order(self, order: OptionOrder) -> dict[str, Any]:
        raise NotImplementedError(
            "Alpaca option order execution is not yet enabled. "
            "Complete paper-mode validation and confirm account options approval first."
        )

    async def close_option_position(self, option_symbol: str) -> dict[str, Any]:
        raise NotImplementedError("Alpaca option close not yet implemented")

    async def get_option_position(self, option_symbol: str) -> dict[str, Any] | None:
        raise NotImplementedError("Alpaca option position lookup not yet implemented")
