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


async def options_paper_active(db: AsyncSession, settings) -> tuple[str, str, int] | None:
    """Return (api_key, api_secret, owner_user_id) when ``auto_paper_options`` is
    enabled AND the separate options keys are configured; else None.

    The owner user id is the bookkeeping account holder for the BrokerOrder rows
    (broker_orders.user_id is NOT NULL in the DB); the *trading* account is the
    separate Alpaca credentials.
    """
    from models import AppSettings, User

    srow = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    data = (srow.data or {}) if srow else {}
    if not data.get("auto_paper_options"):
        return None
    creds = options_paper_credentials(settings)
    if not creds:
        return None
    owner_id = (await db.execute(select(User.id).where(User.is_owner == True).order_by(User.id))).scalars().first()
    if owner_id is None:
        return None
    return creds[0], creds[1], owner_id


# BrokerOrder.status CheckConstraint allows only this set; Alpaca returns richer
# statuses (accepted/new/pending_new/partially_filled/...), so normalize.
_ALLOWED_STATUSES = {"submitted", "filled", "rejected", "error", "orphan", "canceled"}


def _normalize_status(raw: str | None) -> str:
    s = (raw or "").lower()
    if s in _ALLOWED_STATUSES:
        return s
    if s in ("canceled", "cancelled", "expired"):
        return "canceled"
    if s == "rejected":
        return "rejected"
    if s == "error":
        return "error"
    # accepted / new / pending_new / accepted_for_bidding / partially_filled / etc.
    return "submitted"


def options_paper_credentials(settings) -> tuple[str, str] | None:
    """Return (api_key, api_secret) for the dedicated options Alpaca paper account,
    or None when not configured. These are SEPARATE from the equity account keys —
    no fallback, so options orders never accidentally hit the equity account."""
    key = settings.alpaca_options_api_key.get_secret_value() if settings.alpaca_options_api_key else ""
    secret = settings.alpaca_options_api_secret.get_secret_value() if settings.alpaca_options_api_secret else ""
    return (key, secret) if key and secret else None


def _order_from_signal(sig: dict[str, Any]) -> OptionOrder | None:
    """Build an OptionOrder from a VRP signal dict's option_legs."""
    strategy = sig.get("option_strategy")
    raw_legs = sig.get("option_legs") or []
    symbol = (sig.get("ticker") or "").upper()
    if not strategy or not raw_legs or not symbol:
        return None
    legs: list[OptionLeg] = []
    for leg in raw_legs:
        position = leg.get("position", "long")
        side_raw = leg.get("side", "")
        side = side_raw if side_raw in ("buy", "sell") else ("buy" if position == "long" else "sell")
        legs.append(
            OptionLeg(
                side=side,
                position=position,
                option_symbol=leg.get("option_symbol", ""),
                quantity=int(leg.get("quantity", 1)),
                strike=float(leg.get("strike", 0.0)),
                expiry=str(leg.get("expiry", "")),
            )
        )
    if not legs:
        return None
    return OptionOrder(
        underlying=symbol,
        strategy=strategy,
        legs=legs,
        max_loss=float(sig.get("option_max_loss") or 0.0),
        expected_gain=float(sig.get("option_exp_gain") or 0.0),
    )


async def submit_paper_option_order(
    sig: dict[str, Any],
    signal_id: int | None,
    db: AsyncSession,
    api_key: str,
    api_secret: str,
    account_user_id: int,
) -> BrokerOrder | None:
    """Submit one VRP signal to the dedicated Alpaca options PAPER account.

    Records a ``BrokerOrder`` with ``broker='alpaca_options'``, ``account_type=
    'paper'``. Idempotent per open position: skips if a non-rejected order already
    covers the same first leg for this underlying (re-emit / restart guard).
    Returns the BrokerOrder or None when skipped/ineligible.
    """
    from sqlalchemy import or_

    from services.brokers.alpaca_options import AlpacaOptionsBroker

    order = _order_from_signal(sig)
    if order is None:
        return None

    # Skip malformed multi-leg structures (mismatched expiries / duplicate
    # contracts from independent chain resolution) — Alpaca 422s otherwise. Guards
    # pre-existing signals built before the options_engine fix.
    if len(order.legs) > 1:
        _syms = [leg.option_symbol for leg in order.legs]
        _exps = {leg.expiry for leg in order.legs}
        if len(set(_syms)) != len(_syms) or len(_exps) != 1:
            log.info(
                "options paper: skipping malformed %s legs for %s (expiries=%s)",
                order.strategy,
                order.underlying,
                sorted(_exps),
            )
            return None
    symbol = order.underlying
    first_sym = order.legs[0].option_symbol

    existing = (
        (
            await db.execute(
                select(BrokerOrder).where(
                    BrokerOrder.broker == "alpaca_options",
                    BrokerOrder.symbol == symbol,
                    or_(BrokerOrder.status.is_(None), BrokerOrder.status != "rejected"),
                )
            )
        )
        .scalars()
        .all()
    )
    for o in existing:
        if any((lf or {}).get("option_symbol") == first_sym for lf in (o.option_legs or [])):
            return None  # already holding this position

    order_record = BrokerOrder(
        signal_id=signal_id,
        user_id=account_user_id,  # bookkeeping holder; trading account = options creds
        broker="alpaca_options",
        account_type="paper",
        symbol=symbol,
        notional=round(float(sig.get("option_max_loss") or 0.0), 2),
        side="sell" if order.strategy.startswith("SELL") else "buy",
        status="submitted",
        arrival_price=float(sig.get("entry") or sig.get("price") or 0.0),
        route_order_type="market",
        requested_qty=sum(leg.quantity for leg in order.legs),
        option_legs=[leg.__dict__ for leg in order.legs],
    )
    try:
        broker = AlpacaOptionsBroker(api_key=api_key, api_secret=api_secret, paper=True)
        result = await broker.place_option_order(order)
        order_record.alpaca_order_id = result.get("alpaca_order_id")
        order_record.status = _normalize_status(result.get("status"))
        if order_record.status in ("error", "rejected"):
            order_record.error_msg = (result.get("reason") or "")[:500]
            order_record.reject_reason = (result.get("reason") or "")[:500]
        log.info(
            "options paper order: %s %s -> %s (%s)", symbol, order.strategy, order_record.status, result.get("status")
        )
    except Exception as exc:
        order_record.status = "error"
        order_record.error_msg = str(exc)[:500]
        log.warning("options paper order failed for %s: %s", symbol, exc)
    db.add(order_record)
    await db.flush()
    return order_record


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
