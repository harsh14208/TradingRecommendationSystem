"""
services/portfolio_allocator.py

QENG-4a: Portfolio allocator service.
QENG-4b: Hierarchical Risk Parity (HRP) baseline.
QENG-4c: Cost-aware turnover control (no-trade bands).

Calculates covariance, groups assets hierarchically, and recursively bisects risk
to allocate weights. Filters allocations through sector, cash, and turnover bounds.
"""

import logging
import os
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models import Instrument, Position, Fill, BrokerOrder, PnlDaily

from services.market_data import get_histories_batch, get_history
from services.tca_service import calculate_expected_slippage_bps

# Maximum allowed expected implementation shortfall (bps) before sizing down.
# Set to 20 bps by default per §118; override via environment if needed.
_ALLOCATOR_SLIPPAGE_THRESHOLD_BPS = float(os.getenv("TCA_SLIPPAGE_THRESHOLD_BPS", "20.0"))

# Residual cash overlay configuration (see docs/RUNBOOK.md §Cash overlay)
_CASH_OVERLAY_ENABLE = os.getenv("CASH_OVERLAY_ENABLE", "false").lower() in ("1", "true", "yes", "on")
_CASH_OVERLAY_TICKER = os.getenv("CASH_OVERLAY_TICKER", "SGOV").strip().upper()
_CASH_OVERLAY_BETA_TICKER = os.getenv("CASH_OVERLAY_BETA_TICKER", "VOO").strip().upper()
_CASH_OVERLAY_MAX_FRACTION = float(os.getenv("CASH_OVERLAY_MAX_FRACTION", "0.50"))
_CASH_OVERLAY_VIX_THRESHOLD = float(os.getenv("CASH_OVERLAY_VIX_THRESHOLD", "18.0"))
_CASH_OVERLAY_MIN_TRADE_DOLLARS = float(os.getenv("CASH_OVERLAY_MIN_TRADE_DOLLARS", "100.0"))

log = logging.getLogger("signal.trade.allocator")


async def _latest_vix() -> float | None:
    """Fetch the most recent daily close for the VIX index."""
    try:
        df = await get_history("^VIX", period="5d", interval="1d")
        if df is not None and not df.empty and "Close" in df.columns:
            return float(df["Close"].dropna().iloc[-1])
    except Exception as e:
        log.warning(f"Failed to fetch VIX for overlay decision: {e}")
    return None


# Constants for allocator bounds
MAX_SECTOR_EXPOSURE = 0.35  # max 35% in any single sector
MAX_SINGLE_STOCK = 0.15  # max 15% in any single stock
TURNOVER_NO_TRADE_BAND = 0.02  # 2% no-trade band (cost-aware control)

# R7: graduated drawdown throttle for new positions. Calibrated in 26-year
# backtest (2000-2026): trigger >3% off peak, scale new positions to 0.5×.
_DD_THROTTLE_TRIGGER_PCT = float(os.getenv("DD_THROTTLE_TRIGGER_PCT", "3.0"))
_DD_THROTTLE_MULT = float(os.getenv("DD_THROTTLE_MULT", "0.5"))


def compute_dd_multiplier(drawdown_pct: float) -> float:
    """
    R7 graduated de-risk: scale new positions when portfolio is below peak.

    Defaults mirror the 26yr honest canon (2000-2026, PIT-corrected
    membership, N=313): Ann.Sharpe 3.28 -> 3.46 and max DD -8.43% -> -6.38%
    at zero CAGR cost. (An earlier pre-PIT-fix run reported 3.01 -> 3.40 on
    a contaminated 332-trade universe; see docs/RESEARCH_SIGNAL_ENGINE_IMPROVEMENTS.md.)
    """
    if drawdown_pct <= _DD_THROTTLE_TRIGGER_PCT:
        return 1.0
    return _DD_THROTTLE_MULT


def get_correlation_matrix(cov: np.ndarray) -> np.ndarray:
    """Derive correlation matrix from covariance matrix."""
    diag = np.diag(cov)
    std = np.sqrt(diag)
    std[std == 0] = 1.0
    outer = np.outer(std, std)
    corr = cov / outer
    corr = np.clip(corr, -1.0, 1.0)
    return corr


def single_linkage_clustering(corr: np.ndarray) -> list[list[int]]:
    """
    Stage 1: Hierarchical tree clustering using single linkage.
    Returns a linkage list representing the dendrogram.
    """
    n = corr.shape[0]
    # Distance matrix: d(i, j) = sqrt(2 * (1 - rho(i, j)))
    dist = np.sqrt(np.clip(2 * (1.0 - corr), 0.0, 4.0))
    np.fill_diagonal(dist, np.inf)

    # Active clusters list of dict: each has {"id": int, "elements": list[int]}
    active = [{"id": i, "elements": [i]} for i in range(n)]
    linkage = []
    cluster_counter = n

    while len(active) > 1:
        # Find minimum distance between any element in active clusters
        min_d = np.inf
        u_idx, v_idx = -1, -1

        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                c1_elems = active[i]["elements"]
                c2_elems = active[j]["elements"]
                d_c1_c2 = np.min(dist[np.ix_(c1_elems, c2_elems)])
                if d_c1_c2 < min_d:
                    min_d = d_c1_c2
                    u_idx, v_idx = i, j

        # Merge active[u_idx] and active[v_idx]
        c_u = active[u_idx]
        c_v = active[v_idx]

        merged_elements = c_u["elements"] + c_v["elements"]
        new_id = cluster_counter
        cluster_counter += 1

        # Record link using their unique cluster IDs
        linkage.append([c_u["id"], c_v["id"], min_d, len(merged_elements)])

        # Replace c_u with the new merged cluster, and remove c_v
        active[u_idx] = {"id": new_id, "elements": merged_elements}
        active.pop(v_idx)

    return linkage


def quasi_diagonalize(linkage: list[list[int]], n: int) -> list[int]:
    """
    Stage 2: Quasi-diagonalization.
    Reorders the covariance matrix so that similar items are adjacent.
    """
    if not linkage:
        return [0]

    # Reconstruct the tree traversal
    tree = {i: [i] for i in range(n)}
    next_node = n

    for link in linkage:
        c_u, c_v = link[0], link[1]
        tree[next_node] = tree[c_u] + tree[c_v]
        next_node += 1

    return tree[next_node - 1]


def get_cluster_var(cov: np.ndarray, cluster: list[int]) -> float:
    """Compute the variance of a cluster using inverse-variance allocation."""
    cov_slice = cov[np.ix_(cluster, cluster)]
    diag = np.diag(cov_slice)

    # Inverse variance weights
    inv_var = 1.0 / diag
    inv_var[np.isinf(inv_var)] = 0.0
    if inv_var.sum() == 0:
        inv_var = np.ones_like(diag)

    w = inv_var / inv_var.sum()
    cluster_var = np.dot(w, np.dot(cov_slice, w))
    return float(cluster_var)


def recursive_bisection(cov: np.ndarray, sort_items: list[int]) -> np.ndarray:
    """
    Stage 3: Recursive bisection weight allocation.
    Inversely allocates weight based on cluster variance.
    """
    weights = np.ones(cov.shape[0])

    # Queue of clusters to split: (items list, current weight multiplier)
    queue = [(sort_items, 1.0)]

    while queue:
        items, w_mult = queue.pop(0)
        if len(items) <= 1:
            weights[items[0]] = w_mult
            continue

        # Split items list in half
        mid = len(items) // 2
        left = items[:mid]
        right = items[mid:]

        # Calculate cluster variances
        var_l = get_cluster_var(cov, left)
        var_r = get_cluster_var(cov, right)

        # Compute allocation factor alpha (inverse volatility/variance weighting)
        if var_l + var_r == 0:
            alpha = 0.5
        else:
            alpha = 1.0 - (var_l / (var_l + var_r))

        # Push children to queue
        queue.append((left, w_mult * alpha))
        queue.append((right, w_mult * (1.0 - alpha)))

    return weights


def compute_hrp_weights(cov: np.ndarray, tickers: list[str]) -> dict[str, float]:
    """
    Compute Hierarchical Risk Parity weights for a given covariance matrix.
    Falls back to equal weight if there are fewer than 2 assets or if covariance is singular.
    """
    n = len(tickers)
    if n == 0:
        return {}
    if n == 1:
        return {tickers[0]: 1.0}

    try:
        corr = get_correlation_matrix(cov)
        linkage = single_linkage_clustering(corr)
        sort_items = quasi_diagonalize(linkage, n)
        raw_weights = recursive_bisection(cov, sort_items)

        # Normalize weights to sum to 1.0
        normalized = raw_weights / raw_weights.sum()
        return {tickers[i]: float(normalized[i]) for i in range(n)}
    except Exception as e:
        log.warning(f"HRP calculation failed: {e}. Falling back to Equal Weight.", exc_info=True)
        return {t: 1.0 / n for t in tickers}


async def fetch_historical_covariance(db: AsyncSession, tickers: list[str], lookback_days: int = 90) -> np.ndarray:
    """Fetch daily returns for lookback window and calculate covariance matrix."""
    n = len(tickers)
    if n < 2:
        return np.eye(max(1, n))

    try:
        histories = await get_histories_batch(tickers, period="6mo", interval="1d")
        returns_cols = {}
        min_rows = 20

        for t in tickers:
            df = histories.get(t)
            if df is None or len(df) < min_rows:
                continue
            closes = df["Close"].astype(float).values[-lookback_days:]
            # Calculate simple returns
            rets = np.diff(closes) / closes[:-1]
            returns_cols[t] = rets

        # Align rows of returns
        valid_tickers = [t for t in tickers if t in returns_cols]
        if len(valid_tickers) < 2:
            return np.eye(n)

        min_len = min(len(v) for v in returns_cols.values())
        R = np.column_stack([returns_cols[t][-min_len:] for t in valid_tickers])

        # Covariance matrix (annualized daily covariance)
        cov = np.cov(R.T) * 252

        # Re-map covariance back to full input tickers list (filling zeros/eye for missing)
        full_cov = np.eye(n) * 0.01  # small base variance
        ticker_to_idx = {t: i for i, t in enumerate(tickers)}

        for i, t1 in enumerate(valid_tickers):
            for j, t2 in enumerate(valid_tickers):
                idx1 = ticker_to_idx[t1]
                idx2 = ticker_to_idx[t2]
                val = cov[i, j] if len(valid_tickers) > 1 else cov
                full_cov[idx1, idx2] = val

        return full_cov
    except Exception as e:
        log.error(f"Failed to fetch historical covariance: {e}")
        return np.eye(n) * 0.05


async def fetch_realized_slippage_avg(db: AsyncSession, lookback_days: int = 30) -> dict[str, float]:
    """Fetch historical average realized slippage (bps) per symbol in the lookback window."""
    try:
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        stmt = (
            select(BrokerOrder.symbol, func.avg(Fill.slippage_bps))
            .join(BrokerOrder, Fill.broker_order_id == BrokerOrder.id)
            .where(Fill.filled_at >= cutoff)
            .group_by(BrokerOrder.symbol)
        )
        res = await db.execute(stmt)
        return {symbol: float(avg) for symbol, avg in res.all() if avg is not None}
    except Exception as e:
        log.warning(f"Failed to fetch realized slippage avg: {e}")
        return {}


async def _add_overlay_orders(
    orders: list[dict],
    final_weights: dict[str, float],
    current_weights: dict[str, float],
    total_cash: float,
    dd_mult: float,
) -> list[dict]:
    """Add orders to deploy residual cash into a parking or beta vehicle.

    The overlay invests any capital the engine did not allocate to active signals.
    By default residual cash goes into a T-bill ETF (SGOV). When VIX is below the
    configured threshold and the account is not in a drawdown throttle, the residual
    can be rotated into a low-cost S&P 500 ETF (VOO) for incremental beta.
    """
    if not _CASH_OVERLAY_ENABLE or not _CASH_OVERLAY_TICKER:
        return orders

    deployed_weight = sum(final_weights.values())
    residual_weight = max(0.0, 1.0 - deployed_weight)
    if residual_weight <= 0 and not current_weights:
        return orders

    # Choose target overlay ticker. Beta sleeve is only used when calm.
    vix = await _latest_vix()
    use_beta = _CASH_OVERLAY_BETA_TICKER and dd_mult >= 1.0 and vix is not None and vix <= _CASH_OVERLAY_VIX_THRESHOLD
    overlay_tickers = {_CASH_OVERLAY_TICKER, _CASH_OVERLAY_BETA_TICKER}
    target_ticker = _CASH_OVERLAY_BETA_TICKER if use_beta else _CASH_OVERLAY_TICKER

    # Do not overlay a ticker that the engine is actively managing this cycle.
    if target_ticker in final_weights:
        log.info(f"Cash overlay: skipping {target_ticker} because engine already has a target weight")
        return orders

    # Cap overlay exposure.
    target_overlay_weight = min(residual_weight, _CASH_OVERLAY_MAX_FRACTION)
    current_overlay_weight = current_weights.get(target_ticker, 0.0)
    overlay_diff_weight = target_overlay_weight - current_overlay_weight
    overlay_diff_dollars = overlay_diff_weight * total_cash

    # Close any existing overlay position that is no longer the target.
    for t, w in list(current_weights.items()):
        if t in overlay_tickers and t != target_ticker and w > 0:
            close_dollars = w * total_cash
            if close_dollars >= _CASH_OVERLAY_MIN_TRADE_DOLLARS:
                orders.append(
                    {
                        "ticker": t,
                        "action": "SELL",
                        "notional": round(close_dollars, 2),
                        "target_weight": 0.0,
                        "expected_slippage": 0.0,
                        "signal_id": None,
                    }
                )
                log.info(f"Cash overlay: closing {t} to switch into {target_ticker}")

    if abs(overlay_diff_dollars) <= _CASH_OVERLAY_MIN_TRADE_DOLLARS + 1e-6:
        return orders

    action = "BUY" if overlay_diff_dollars > 0 else "SELL"
    orders.append(
        {
            "ticker": target_ticker,
            "action": action,
            "notional": round(abs(overlay_diff_dollars), 2),
            "target_weight": round(target_overlay_weight, 4),
            "expected_slippage": 0.0,
            "signal_id": None,
        }
    )
    log.info(
        f"Cash overlay: {action} ${abs(overlay_diff_dollars):,.2f} of {target_ticker} "
        f"(weight {current_overlay_weight:.2%} -> {target_overlay_weight:.2%}, VIX={vix})"
    )
    return orders


async def allocate_portfolio(
    db: AsyncSession, user_id: int, active_signals: list[dict], total_cash: float
) -> list[dict]:
    """
    QENG-4a: Portfolio allocator service.
    Translates signals into size-optimized orders utilizing HRP,
    honoring constraints (max sector, max single stock) and cost-aware turnover bands.
    Optimized with Drawdown Throttle, L7 Sizing Nudge, and Volatility Sizing Penalty.
    """
    if not active_signals or total_cash <= 0:
        return []

    tickers = [s["ticker"] for s in active_signals]

    # 1. Fetch covariance & compute HRP weights
    cov = await fetch_historical_covariance(db, tickers)
    hrp_weights = compute_hrp_weights(cov, tickers)

    # Fetch histories for Volatility Sizing Penalty (ATR%)
    histories = await get_histories_batch(tickers, period="6mo", interval="1d")

    atr_pcts = {}
    for t in tickers:
        df = histories.get(t)
        if df is not None and len(df) >= 20:
            high = df["High"].astype(float).values
            low = df["Low"].astype(float).values
            close = df["Close"].astype(float).values

            # Compute rolling ATR (20)
            tr = np.zeros(len(close))
            tr[0] = high[0] - low[0]
            for i in range(1, len(close)):
                tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
            atr_20 = np.mean(tr[-20:])
            latest_close = close[-1]
            if latest_close > 0:
                atr_pcts[t] = float(atr_20 / latest_close) * 100.0
            else:
                atr_pcts[t] = 2.0
        else:
            atr_pcts[t] = 2.0

    # Volatility Sizing Penalty: top 33% (67th percentile) threshold
    if len(atr_pcts) >= 3:
        atr_threshold = np.percentile(list(atr_pcts.values()), 67)
    else:
        atr_threshold = 3.0

    # Fetch historical realized slippage for feedback (REF-1)
    realized_slippage = await fetch_realized_slippage_avg(db)

    # Fetch current positions to map current weights and identify if ticker is new
    res_pos = await db.execute(select(Position).where(Position.user_id == user_id).where(Position.qty > 0))
    current_positions = res_pos.scalars().all()

    current_weights = {}
    for p in current_positions:
        res_inst = await db.execute(select(Instrument).where(Instrument.id == p.instrument_id))
        inst = res_inst.scalar_one_or_none()
        if inst:
            pos_value = p.qty * (p.average_entry_price or 100.0)
            current_weights[inst.ticker] = pos_value / total_cash

    # 2. Apply constraints (Max single stock limit, slippage, L7, and vol-scaled penalty)
    constrained_weights = {}
    for t, w in hrp_weights.items():
        weight = w
        if t in realized_slippage:
            slippage_bps = realized_slippage[t]
            penalty_multiplier = max(0.0, 1.0 - (slippage_bps / _ALLOCATOR_SLIPPAGE_THRESHOLD_BPS))
            weight *= penalty_multiplier
            log.info(
                f"TCA feedback: {t} weight scaled by {penalty_multiplier:.2f} due to {slippage_bps:.1f} bps average realized slippage."
            )

        # L7 Score-Weighted Sizing (Inv2)
        score = 50.0
        sig = next((s for s in active_signals if s["ticker"] == t), None)
        if sig:
            score = sig.get("raw_score") or sig.get("score") or sig.get("confidence") or 50.0
        scale_l7 = max(0.85, min(1.15, 0.85 + (score - 50) / 100))

        # Volatility Sizing Penalty (R10-8)
        atr_val = atr_pcts.get(t, 2.0)
        vol_mult = 0.7 if atr_val >= atr_threshold else 1.0

        weight *= scale_l7 * vol_mult

        log.info(
            f"Allocator weight adjustment for {t}: base_w={w:.4f}, L7={scale_l7:.2f}, vol_mult={vol_mult:.2f} (ATR%={atr_val:.2f}%), adjusted_w={weight:.4f}"
        )

        constrained_weights[t] = min(weight, MAX_SINGLE_STOCK)

    # Renormalize
    w_sum = sum(constrained_weights.values())
    if w_sum > 0:
        constrained_weights = {t: w / w_sum for t, w in constrained_weights.items()}

    # 3. Apply sector concentration limits
    # Fetch sectors for tickers
    sector_map = {}
    for s in active_signals:
        sector_map[s["ticker"]] = s.get("sectorEtf") or "XLK"  # default XLK

    sector_exposure = {}
    for t, w in constrained_weights.items():
        sect = sector_map[t]
        sector_exposure[sect] = sector_exposure.get(sect, 0.0) + w

    # Calculate dynamic sector limits using covariance-based HRP weights
    # Base HRP weights are already correlation-aware.
    # We define limit per sector = hrp_sector_weight + 0.10, clamped between 20% and 40%
    hrp_sector_weights = {}
    for t, w in hrp_weights.items():
        sect = sector_map[t]
        hrp_sector_weights[sect] = hrp_sector_weights.get(sect, 0.0) + w

    dynamic_sector_limits = {}
    for sect in sector_exposure:
        hrp_w = hrp_sector_weights.get(sect, 0.0)
        # Limit scales off HRP weight, allowing a buffer but capping at 40%
        dynamic_limit = max(0.20, min(0.40, hrp_w + 0.10))
        dynamic_sector_limits[sect] = dynamic_limit
        log.info(f"Dynamic sector limit for {sect}: HRP weight = {hrp_w:.4f} -> Limit = {dynamic_limit:.2f}")

    # Scale down weights of overallocated sectors
    over_allocated = {}
    for sect, w in sector_exposure.items():
        limit = dynamic_sector_limits.get(sect, MAX_SECTOR_EXPOSURE)
        if w > limit:
            over_allocated[sect] = (w, limit)

    if over_allocated:
        for t in list(constrained_weights.keys()):
            sect = sector_map[t]
            if sect in over_allocated:
                curr_w, limit = over_allocated[sect]
                scale_factor = limit / curr_w
                constrained_weights[t] *= scale_factor
        # Renormalize
        w_sum = sum(constrained_weights.values())
        if w_sum > 0:
            constrained_weights = {t: w / w_sum for t, w in constrained_weights.items()}

    # 4. Cost-aware turnover control (QENG-4c: no-trade bands)
    # Apply turnover control (no-trade band check)
    final_weights = {}
    for t in constrained_weights:
        target = constrained_weights[t]
        current = current_weights.get(t, 0.0)

        # If difference is within 2%, keep current weight (or 0 if not holding) to avoid churn
        if abs(target - current) < TURNOVER_NO_TRADE_BAND:
            final_weights[t] = current
            log.info(
                f"Turnover control: {t} weight change ({current:.2f} -> {target:.2f}) is inside 2% band. Retaining {current:.2f}."
            )
        else:
            final_weights[t] = target

    # 5. Drawdown Throttle (R7)
    # If the user is in drawdown from historical peak equity, scale new positions.
    dd_mult = 1.0
    dd_pct = 0.0
    try:
        stmt = select(func.max(PnlDaily.equity)).where(PnlDaily.user_id == user_id)
        res = await db.execute(stmt)
        peak_equity = res.scalar()
        if peak_equity is not None and peak_equity > 0:
            dd_pct = (peak_equity - total_cash) / peak_equity * 100.0
            dd_mult = compute_dd_multiplier(dd_pct)
            if dd_mult < 1.0:
                log.info(
                    f"Drawdown Throttle active: user={user_id} is in {dd_pct:.2f}% drawdown "
                    f"(peak=${peak_equity:,.2f}, current=${total_cash:,.2f}). "
                    f"Scaling new trades by {dd_mult:.2f}."
                )
    except Exception as e:
        log.warning(f"Failed to query peak equity for drawdown throttle: {e}")

    if dd_mult < 1.0:
        for t in list(final_weights.keys()):
            is_new = t not in current_weights or current_weights[t] <= 0.0
            if is_new:
                old_w = final_weights[t]
                final_weights[t] *= dd_mult
                log.info(
                    f"Drawdown Throttle: scaled new position {t} target weight from {old_w:.4f} to {final_weights[t]:.4f}"
                )

    # Renormalize final weights (only cap leverage at 1.0, do not force sum to 1.0 if we scaled down)
    w_sum = sum(final_weights.values())
    if w_sum > 1.0:  # leverage cap
        final_weights = {t: w / w_sum for t, w in final_weights.items()}

    # Translate final weights to target order directions and dollar sizes
    orders_to_place = []
    for s in active_signals:
        t = s["ticker"]
        target_w = final_weights.get(t, 0.0)
        current_w = current_weights.get(t, 0.0)

        target_notional = target_w * total_cash
        current_notional = current_w * total_cash
        diff_notional = target_notional - current_notional

        if abs(diff_notional) > 5.0:  # minimum trade size $5
            # Expected slippage for the target order using Almgren-Chriss + realized floor.
            entry_price = s.get("entry") or 100.0
            qty = abs(diff_notional) / entry_price if entry_price > 0 else 0.0
            ticker_slippage = calculate_expected_slippage_bps(
                t,
                qty=qty,
                price=entry_price,
                adv=10_000_000 if t in ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "TSLA"] else 500_000,
                daily_vol=0.018 if t in ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "TSLA"] else 0.035,
                spread_pct=0.0003 if t in ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "TSLA"] else 0.0018,
                realized_slippage_bps=realized_slippage.get(t),
            )
            orders_to_place.append(
                {
                    "ticker": t,
                    "action": "BUY" if diff_notional > 0 else "SELL",
                    "notional": round(abs(diff_notional), 2),
                    "target_weight": round(target_w, 4),
                    "expected_slippage": round(ticker_slippage, 2),
                    "signal_id": s.get("id"),
                }
            )

    # 6. Residual cash overlay (cash/beta parking)
    if _CASH_OVERLAY_ENABLE:
        orders_to_place = await _add_overlay_orders(
            orders_to_place,
            final_weights,
            current_weights,
            total_cash,
            dd_mult,
        )

    return orders_to_place
