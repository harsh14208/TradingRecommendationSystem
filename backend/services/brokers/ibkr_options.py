"""IBKR options-order broker stub.

Implements the ``OptionsBroker`` interface but raises ``NotImplementedError``
until IBKR integration is prioritized.  This preserves the broker-agnostic shape
of ``services/broker_svc.py``.
"""

from __future__ import annotations

from typing import Any

from services.brokers.options_broker import OptionOrder, OptionsBroker


class IBKROptionsBroker(OptionsBroker):
    name = "ibkr"

    def __init__(self, bearer_token: str, account_id: str | None = None) -> None:
        self.bearer_token = bearer_token
        self.account_id = account_id

    async def place_option_order(self, order: OptionOrder) -> dict[str, Any]:
        raise NotImplementedError("IBKR option order execution is not yet implemented")

    async def close_option_position(self, option_symbol: str) -> dict[str, Any]:
        raise NotImplementedError("IBKR option close not yet implemented")

    async def get_option_position(self, option_symbol: str) -> dict[str, Any] | None:
        raise NotImplementedError("IBKR option position lookup not yet implemented")
