"""Paper-trade simulation for option strategies.

Simulates fills at the natural side of the spread (buy at ask, sell at bid),
books a ``BrokerOrder`` with status ``filled``, and resolves P&L nightly against
Polygon option snapshots.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import BrokerOrder
from services.brokers.options_broker import OptionLeg, OptionOrder
from services.options_chain_resolver import (
    OptionContract,
    fetch_contract_snapshot,
    natural_fill_price,
)
from services.massive_options_data import _parse_opra
from services.options_engine import _is_leveraged

log = logging.getLogger("signal.options_paper")

_OPTION_FEE_PER_CONTRACT = 0.65


def _underlying_from_symbol(option_symbol: str) -> str | None:
    parsed = _parse_opra(option_symbol)
    return parsed[0] if parsed else None


async def _get_contract(leg: OptionLeg) -> OptionContract | None:
    """Fetch a real-time contract snapshot for a leg."""
    underlying = _underlying_from_symbol(leg.option_symbol)
    if not underlying:
        return None
    return await fetch_contract_snapshot(underlying, leg.option_symbol)


def _order_side_from_strategy(strategy: str) -> str:
    """Map an option strategy to a BrokerOrder side."""
    return "buy" if strategy == "LONG_STRADDLE" else "sell"


async def simulate_fill(
    order: OptionOrder,
    signal: dict[str, Any],
    db: AsyncSession,
) -> BrokerOrder:
    """Record a paper fill for an option order.

    Fills are simulated at the natural side of the spread.  The resulting
    ``BrokerOrder`` has ``broker='paper_options'`` and ``status='filled'``.
    """
    if _is_leveraged(order.underlying):
        log.warning("paper_options: leveraged ETF %s blocked from simulation", order.underlying)
        raise ValueError(f"Leveraged ETF {order.underlying} is not eligible for options paper simulation")

    leg_fills: list[dict[str, Any]] = []
    total_qty = 0
    entry_premium = 0.0  # per-share premium sum across legs
    total_notional = 0.0

    for leg in order.legs:
        contract = await _get_contract(leg)
        if contract is None:
            log.warning(
                "Paper fill for %s: could not resolve contract %s, using mid from signal",
                order.underlying,
                leg.option_symbol,
            )
            fill_price = 0.0
        else:
            fill_price = natural_fill_price(contract, leg.position, leg.side)

        leg_value = fill_price * leg.quantity
        multiplier = 1 if leg.position == "long" else -1
        signed_value = leg_value * multiplier

        total_qty += leg.quantity
        entry_premium += signed_value
        total_notional += leg_value * 100.0

        leg_fills.append(
            {
                "option_symbol": leg.option_symbol,
                "option_type": leg.option_symbol[-9] if len(leg.option_symbol) >= 9 else None,
                "position": leg.position,
                "side": leg.side,
                "quantity": leg.quantity,
                "strike": leg.strike,
                "expiry": leg.expiry,
                "entry_fill": round(fill_price, 4),
                "entry_mid": round(contract.midpoint, 4) if contract else None,
                "entry_bid": round(contract.bid, 4) if contract else None,
                "entry_ask": round(contract.ask, 4) if contract else None,
            }
        )

    fees = _OPTION_FEE_PER_CONTRACT * total_qty
    avg_fill_price = total_notional / (total_qty * 100.0) if total_qty else 0.0

    order_record = BrokerOrder(
        signal_id=signal.get("signal_id"),
        user_id=signal.get("user_id"),
        broker="paper_options",
        account_type="paper",
        symbol=order.underlying.upper(),
        notional=round(total_notional, 2),
        side=_order_side_from_strategy(order.strategy),
        status="filled",
        arrival_price=float(signal.get("entry") or signal.get("price") or 0.0),
        route_order_type="market",
        requested_qty=total_qty,
        filled_qty=total_qty,
        avg_fill_price=round(avg_fill_price, 4),
        fees=round(fees, 2),
        option_legs=leg_fills,
        realized_pnl=-fees,  # start with fees paid; P&L adds as mark moves
    )
    db.add(order_record)
    await db.flush()
    log.info(
        "paper_options fill: %s %s qty=%d notional=%.2f fees=%.2f",
        order.underlying,
        order.strategy,
        total_qty,
        total_notional,
        fees,
    )
    return order_record


def _leg_pnl(leg_fill: dict[str, Any], current_mid: float) -> float:
    """P&L for one leg given current mid price."""
    entry = float(leg_fill.get("entry_fill") or 0.0)
    qty = int(leg_fill.get("quantity") or 0)
    position = leg_fill.get("position", "long")
    sign = 1.0 if position == "long" else -1.0
    return (current_mid - entry) * qty * 100.0 * sign


async def resolve_paper_pnl(db: AsyncSession) -> None:
    """Mark all open paper option positions to market using Polygon snapshots."""
    from sqlalchemy import or_

    result = await db.execute(
        select(BrokerOrder).where(
            BrokerOrder.broker == "paper_options",
            or_(
                BrokerOrder.final_execution_status.is_(None),
                BrokerOrder.final_execution_status != "closed",
            ),
        )
    )
    orders = result.scalars().all()
    if not orders:
        return

    updated = 0
    for order in orders:
        legs = order.option_legs or []
        if not legs:
            continue
        total_unrealized = 0.0
        for leg_fill in legs:
            option_symbol = leg_fill.get("option_symbol")
            underlying = _underlying_from_symbol(option_symbol) if option_symbol else None
            if not underlying:
                continue
            contract = await fetch_contract_snapshot(underlying, option_symbol)
            if contract is None:
                continue
            total_unrealized += _leg_pnl(leg_fill, contract.midpoint)
        order.unrealized_pnl = round(total_unrealized, 2)
        updated += 1

    await db.commit()
    log.info("Resolved paper P&L for %d option position(s)", updated)


async def close_paper_position(
    order: BrokerOrder,
    db: AsyncSession,
    exit_mid: float | None = None,
) -> BrokerOrder:
    """Close a paper option position and realize P&L."""
    legs = order.option_legs or []
    realized = 0.0
    for leg_fill in legs:
        option_symbol = leg_fill.get("option_symbol")
        underlying = _underlying_from_symbol(option_symbol) if option_symbol else None
        if not underlying:
            continue
        if exit_mid is not None:
            mid = exit_mid
        else:
            contract = await fetch_contract_snapshot(underlying, option_symbol)
            if contract is None:
                continue
            mid = contract.midpoint
        realized += _leg_pnl(leg_fill, mid)

    fees = order.fees or 0.0
    order.realized_pnl = round(realized - fees, 2)
    order.unrealized_pnl = 0.0
    order.final_execution_status = "closed"
    await db.commit()
    log.info(
        "paper_options close: %s realized_pnl=%.2f",
        order.symbol,
        order.realized_pnl,
    )
    return order
