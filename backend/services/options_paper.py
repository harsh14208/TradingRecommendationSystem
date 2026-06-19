"""Paper-trade simulation for option strategies.

Simulates fills at mid/close, books a ``BrokerOrder`` with status ``paper_filled``,
and resolves P&L nightly against Polygon options snapshots or flat files.  Live
broker execution will use the same order shape through ``services/brokers``.
"""

from __future__ import annotations

import logging
from typing import Any

from services.brokers.options_broker import OptionOrder

log = logging.getLogger("signal.options_paper")


async def simulate_fill(order: OptionOrder) -> dict[str, Any]:
    """Record a paper fill for an option order.

    Currently a placeholder: it returns a normalized dict without writing to the
    ledger so the signal-only path can be exercised end-to-end first.
    """
    log.info(
        "paper fill: %s %s %d legs (max_loss=%.2f exp_gain=%.2f)",
        order.underlying,
        order.strategy,
        len(order.legs),
        order.max_loss,
        order.expected_gain,
    )
    return {
        "status": "paper_filled",
        "broker": "paper",
        "order_id": None,
        "legs": [leg.__dict__ for leg in order.legs],
        "max_loss": order.max_loss,
        "expected_gain": order.expected_gain,
    }


async def resolve_paper_pnl() -> None:
    """Nightly P&L resolution for open paper option positions."""
    log.info("paper P&L resolution not yet implemented")
