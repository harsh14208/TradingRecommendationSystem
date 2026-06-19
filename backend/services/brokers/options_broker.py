"""Abstract broker interface for option-order execution.

Implementations: ``AlpacaOptionsBroker`` (live) and a paper-mode simulator in
``services.options_paper``.  The strategy code talks only to this interface so
Alpaca/IBKR/TDA etc. can be swapped without changing ``services/broker_svc.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OptionLeg:
    side: str  # "buy" | "sell"
    position: str  # "long" | "short"
    option_symbol: str  # OCC format, e.g. O:AAPL260117C00150000
    quantity: int
    strike: float
    expiry: str  # YYYY-MM-DD


@dataclass(frozen=True)
class OptionOrder:
    underlying: str
    strategy: str  # SELL_CASH_SEC_PUT | SELL_STRANGLE | SELL_DEFINED_RISK | LONG_STRADDLE
    legs: list[OptionLeg]
    max_loss: float
    expected_gain: float


class OptionsBroker(ABC):
    """Base class for option-order execution clients."""

    name: str = "abstract"

    @abstractmethod
    async def place_option_order(self, order: OptionOrder) -> dict[str, Any]:
        """Submit an option order and return a normalized fill/status dict."""
        raise NotImplementedError

    @abstractmethod
    async def close_option_position(self, option_symbol: str) -> dict[str, Any]:
        """Close an existing option position by option symbol."""
        raise NotImplementedError

    @abstractmethod
    async def get_option_position(self, option_symbol: str) -> dict[str, Any] | None:
        """Return current position for an option symbol, or None if flat."""
        raise NotImplementedError
