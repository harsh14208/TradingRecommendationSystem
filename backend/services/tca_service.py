"""
services/tca_service.py

QENG-3b: Transaction Cost Analysis service.
QENG-3c: Capacity and participation limits checker.
Computes realized slippage, NBBO spread capture, implementation shortfall,
and checks trading capacity limits before executing orders.
"""

import logging
import math
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import BrokerOrder, Fill, Instrument

log = logging.getLogger("signal.trade.tca")

# Default values if market stats are unavailable
DEFAULT_SPREAD_PCT = 0.0010  # 10 bps
DEFAULT_DAILY_VOL = 0.020   # 2.0%
DEFAULT_ADV = 1_000_000     # 1M shares

async def record_fill_tca(
    db: AsyncSession,
    order: BrokerOrder,
    broker_order_data: dict
) -> BrokerOrder:
    """
    QENG-3b: Extract fill details from broker response and calculate realized TCA.
    Populates NBBO mid, spread, avg_fill_price, fees, slippage_bps, and shortfall.
    """
    try:
        # Extract fields from broker data
        filled_qty = float(broker_order_data.get("filled_qty") or broker_order_data.get("filledQty") or 0.0)
        qty = float(broker_order_data.get("qty") or broker_order_data.get("requested_qty") or order.requested_qty or filled_qty)
        avg_fill_price = float(broker_order_data.get("filled_avg_price") or broker_order_data.get("avg_fill_price") or broker_order_data.get("avgPrice") or 0.0)
        
        # Populate ledger columns
        order.requested_qty = qty
        order.filled_qty = filled_qty
        order.avg_fill_price = avg_fill_price if avg_fill_price > 0 else None
        order.route_order_type = broker_order_data.get("type") or broker_order_data.get("order_type") or "market"
        order.final_execution_status = broker_order_data.get("status")
        
        # Estimate or fetch arrival price (fall back to signal target price or order target)
        if not order.arrival_price:
            order.arrival_price = avg_fill_price  # Fallback
            
        arrival = order.arrival_price
        
        # Calculate NBBO Mid and Spread estimate at arrival if not set
        if not order.nbbo_mid or not order.spread:
            # Estimate spread as 5 bps for liquid tech, 15 bps for others
            spread_pct = 0.0005 if order.symbol in ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"] else 0.0015
            order.spread = round(arrival * spread_pct, 4)
            # Center NBBO mid around arrival price
            order.nbbo_mid = round(arrival, 4)
            
        # Estimate commission/fees (Alpaca paper is free, live has minimal fee, IBKR is ~0.005/share)
        fee_per_share = 0.005 if order.broker == "ibkr" else 0.0001
        order.fees = round(filled_qty * fee_per_share, 2)
        
        if avg_fill_price > 0 and arrival > 0:
            # Slippage = Execution Price - Arrival Price (for BUY)
            # Slippage = Arrival Price - Execution Price (for SELL)
            price_diff = (avg_fill_price - arrival) if order.side.lower() == "buy" else (arrival - avg_fill_price)
            slippage_bps = (price_diff / arrival) * 10000.0
            order.spread = max(order.spread or 0.01, 0.01)
            
            # Spread capture: percentage of bid-ask spread captured/saved.
            # positive = executing better than mid, negative = paying spread.
            # Mid-to-execution diff relative to spread
            mid_diff = (order.nbbo_mid - avg_fill_price) if order.side.lower() == "buy" else (avg_fill_price - order.nbbo_mid)
            order.spread_pct = (mid_diff / order.spread) * 100.0
            
            # Save TCA into BrokerOrder record
            log.info(
                f"TCA recorded for order {order.id} ({order.symbol}): "
                f"Arrival: {arrival:.2f} | Fill: {avg_fill_price:.2f} | "
                f"Slippage: {slippage_bps:.1f} bps | Fees: ${order.fees:.2f}"
            )
            
            # Record individual fill tracking row if missing
            res_fill = await db.execute(
                select(Fill).where(Fill.broker_order_id == order.id)
            )
            existing_fill = res_fill.scalar_one_or_none()
            if not existing_fill and filled_qty > 0:
                res_inst = await db.execute(
                    select(Instrument).where(Instrument.ticker == order.symbol)
                )
                inst = res_inst.scalar_one_or_none()
                new_fill = Fill(
                    broker_order_id=order.id,
                    user_id=order.user_id,
                    instrument_id=inst.id if inst else None,
                    side=order.side,
                    qty=filled_qty,
                    price=avg_fill_price,
                    commission=order.fees or 0.0,
                    slippage_bps=slippage_bps
                )
                db.add(new_fill)
                
    except Exception as e:
        log.error(f"Error recording TCA for order {order.id}: {e}", exc_info=True)
        
    return order

def calculate_expected_slippage_bps(
    ticker: str,
    qty: float,
    price: float,
    adv: float = DEFAULT_ADV,
    daily_vol: float = DEFAULT_DAILY_VOL,
    spread_pct: float = DEFAULT_SPREAD_PCT
) -> float:
    """
    QENG-3c: Almgren-Chriss Market Impact Model.
    Expected Slippage (bps) = 0.5 * Spread (bps) + Volatility * (Quantity / ADV)^0.5
    """
    if adv <= 0:
        adv = DEFAULT_ADV
        
    # Constant coefficient for temporary/permanent impact scale
    impact_coef = 10.0
    
    # Participation rate
    participation = qty / adv
    
    # Half-spread term + market impact term
    half_spread_bps = 0.5 * spread_pct * 10000.0
    impact_bps = impact_coef * daily_vol * math.sqrt(participation) * 10000.0
    
    return half_spread_bps + impact_bps

async def check_capacity_limits(
    db: AsyncSession,
    ticker: str,
    notional: float,
    arrival_price: float
) -> Tuple[bool, float, float]:
    """
    QENG-3c: Capacity and participation limits.
    Blocks or shrinks order size when expected slippage consumes signal edge.
    Expected edge of signal is estimated at 120 bps (typical mean-reversion gain).
    
    Returns:
      (blocked: bool, suggested_notional: float, expected_slippage_bps: float)
    """
    try:
        qty = notional / arrival_price
        
        # Simple lookup for ADV and volatility (can be extended to live fetch from database or daily stats)
        # For this implementation, we use conservative defaults or lookups for liquid tech.
        is_high_liquid = ticker in ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "TSLA"]
        adv = 10_000_000 if is_high_liquid else 500_000
        daily_vol = 0.018 if is_high_liquid else 0.035
        spread_pct = 0.0003 if is_high_liquid else 0.0018
        
        # Calculate expected slippage
        expected_slip = calculate_expected_slippage_bps(ticker, qty, arrival_price, adv, daily_vol, spread_pct)
        
        # Signal edge is roughly 120 bps
        edge_bps = 120.0
        slippage_threshold = 0.35 * edge_bps  # Maximum allowed slippage is 35% of the edge (42 bps)
        
        # Check participation rate limit: max 2% of ADV for any single order
        max_qty = adv * 0.02
        suggested_notional = notional
        blocked = False
        
        if qty > max_qty:
            suggested_notional = max_qty * arrival_price
            qty = max_qty
            log.warning(f"Capacity check: {ticker} order qty {qty:.0f} exceeds 2% ADV limit. Sizing down to {max_qty:.0f} shares.")
            expected_slip = calculate_expected_slippage_bps(ticker, qty, arrival_price, adv, daily_vol, spread_pct)
            
        if expected_slip > slippage_threshold:
            # Expected slippage consumes too much edge. Shrink further or block.
            # Scale down so expected slippage equals the threshold
            allowed_qty = adv * ((slippage_threshold - 0.5 * spread_pct * 10000.0) / (10.0 * daily_vol * 10000.0)) ** 2
            
            if allowed_qty < 1.0 or (allowed_qty * arrival_price) < (0.25 * notional):
                # If suggest sizing down by more than 75%, block trade entirely
                blocked = True
                suggested_notional = 0.0
                log.warning(f"Capacity check: {ticker} BLOCKED. Expected slippage ({expected_slip:.1f} bps) exceeds limit.")
            else:
                suggested_notional = round(allowed_qty * arrival_price, 2)
                log.info(f"Capacity check: {ticker} sized down from ${notional:.2f} to ${suggested_notional:.2f} due to expected slippage ({expected_slip:.1f} bps).")
                
        return blocked, suggested_notional, expected_slip
        
    except Exception as e:
        log.error(f"Error in TCA capacity check: {e}", exc_info=True)
        return False, notional, 10.0
