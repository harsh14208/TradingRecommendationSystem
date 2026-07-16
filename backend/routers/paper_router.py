from config import get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import BrokerOrder, User
from pydantic import BaseModel
from services import alpaca_rest
from services.auth_svc import get_current_user
from services.broker_svc import _normalize_broker_status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/paper", tags=["paper"])


def _require_keys():
    s = get_settings()

    def _unwrap(secret_val):
        if not secret_val:
            return ""
        if hasattr(secret_val, "get_secret_value"):
            return secret_val.get_secret_value() or ""
        return str(secret_val)

    raw_key = _unwrap(s.alpaca_api_key)
    raw_secret = _unwrap(s.alpaca_api_secret)
    if not raw_key or not raw_secret:
        raise HTTPException(403, "Alpaca API keys not configured — set ALPACA_API_KEY and ALPACA_API_SECRET in .env")
    return raw_key, raw_secret


def _require_paper_user(user: User):
    """Paper trading is now available at Basic tier (2026-06-18) as the
    'proof before pay' centerpiece. Pro/Elite get advanced analytics."""
    from config import tier_gte

    if not (user.is_owner or tier_gte(user.subscription_tier, "basic")):
        raise HTTPException(403, "Paper trading requires Basic tier or higher.")


class OrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str  # "buy" | "sell"
    order_type: str = "market"  # "market" | "limit"
    limit_price: float | None = None


@router.get("/account")
async def account(user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    try:
        return await alpaca_rest.get_account(key, secret)
    except alpaca_rest.AlpacaAuthError as e:
        raise HTTPException(401, f"Alpaca authentication failed: {e}")
    except alpaca_rest.AlpacaRateLimitError as e:
        raise HTTPException(429, f"Alpaca rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/options")
async def options_account(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Dedicated options paper account: live account + positions (Alpaca), recent
    submitted orders (broker_orders), and the rolling equity history."""
    _require_paper_user(user)
    from sqlalchemy import desc, select

    from models import AppSettings, Signal
    from services.options_account import compute_options_risk, fetch_options_account, options_pnl_history

    settings = get_settings()
    snap = await fetch_options_account(settings)
    if snap is None:
        return {
            "configured": False,
            "message": "Options paper account not configured — set ALPACA_OPTIONS_API_KEY/SECRET in .env.",
            "account": None,
            "positions": [],
            "orders": [],
            "history": [],
        }

    # Recent options orders + the originating signal's strategy.
    rows = (
        await db.execute(
            select(BrokerOrder, Signal.option_strategy)
            .outerjoin(Signal, Signal.id == BrokerOrder.signal_id)
            .where(BrokerOrder.broker == "alpaca_options")
            .order_by(desc(BrokerOrder.created_at))
            .limit(100)
        )
    ).all()
    orders = [
        {
            "id": o.id,
            "symbol": o.symbol,
            "strategy": strat,
            "side": o.side,
            "status": o.status,
            "qty": o.requested_qty,
            "alpaca_order_id": o.alpaca_order_id,
            "reject_reason": o.reject_reason,
            "legs": o.option_legs or [],
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o, strat in rows
    ]

    srow = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    history = options_pnl_history(srow.data if srow else None)

    try:
        _equity = float((snap["account"] or {}).get("equity") or 0.0)
    except (TypeError, ValueError):
        _equity = 0.0
    risk = await compute_options_risk(snap["positions"], _equity)

    return {
        "configured": True,
        "account": snap["account"],
        "positions": snap["positions"],
        "orders": orders,
        "history": history,
        "risk": risk,
    }


@router.get("/positions")
async def positions(user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    try:
        return await alpaca_rest.get_positions(key, secret)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/orders")
async def orders(status: str = "all", user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    try:
        return await alpaca_rest.get_orders(key, secret, status)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.post("/orders")
async def place_order(
    req: OrderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_paper_user(user)
    key, secret = _require_keys()
    if req.side not in ("buy", "sell"):
        raise HTTPException(400, "side must be 'buy' or 'sell'")
    if req.qty <= 0:
        raise HTTPException(400, "qty must be positive")
    if req.qty > 10_000:
        raise HTTPException(400, "qty cannot exceed 10,000 shares in paper mode")

    order_record = BrokerOrder(
        user_id=user.id,
        broker="alpaca",
        account_type="paper",
        symbol=req.symbol.upper(),
        notional=0.0,
        side=req.side.lower(),
        status="submitted",
    )
    db.add(order_record)
    await db.flush()

    try:
        result = await alpaca_rest.place_order(
            key,
            secret,
            req.symbol,
            req.qty,
            req.side,
            req.order_type,
            req.limit_price,
        )
        order_record.status = _normalize_broker_status(result.get("status"))
        order_record.alpaca_order_id = result.get("id")
    except Exception as e:
        order_record.status = "error"
        order_record.error_msg = str(e)[:500]
        raise HTTPException(502, "Broker request failed")
    finally:
        await db.commit()
    return result


@router.delete("/positions/{symbol}")
async def close_position(symbol: str, user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    try:
        return await alpaca_rest.close_position(key, secret, symbol)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    try:
        return await alpaca_rest.cancel_order(key, secret, order_id)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/risk")
async def portfolio_risk(user: User = Depends(get_current_user)):
    """
    Aggregate risk metrics across all open paper positions:
    Sharpe ratio, max drawdown, beta vs SPY, total exposure.
    """
    _require_paper_user(user)
    import math

    from services.alpaca_rest import get_account, get_positions
    from services.market_data import get_histories_batch

    key, secret = _require_keys()
    positions = []
    account = None
    account_error = None
    try:
        positions = await get_positions(key, secret)
    except Exception as e:
        account_error = str(e)
    try:
        account = await get_account(key, secret)
    except Exception as e:
        account_error = str(e)
    if account_error and not positions and not account:
        raise HTTPException(502, "Broker request failed")

    if not positions:
        return {
            "positions": 0,
            "total_exposure": 0,
            "beta": None,
            "sharpe": None,
            "max_drawdown": None,
            "risk_level": "none",
        }

    tickers = [p["symbol"] for p in positions]
    equity = float(account.get("equity") or 1) if account else 1.0
    histories = await get_histories_batch(tickers + ["SPY"], period="3mo", interval="1d")

    spy_df = histories.get("SPY")
    spy_returns = []
    if spy_df is not None and len(spy_df) > 1:
        closes = spy_df["Close"].astype(float)
        spy_returns = [float(closes.iloc[i] / closes.iloc[i - 1] - 1) for i in range(1, len(closes))]

    betas, pos_returns_by_day = [], {}
    total_exposure = 0.0

    for p in positions:
        sym = p["symbol"]
        mktval = float(p.get("market_value") or 0)
        total_exposure += abs(mktval)
        df = histories.get(sym)
        if df is None or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        daily_ret = [float(closes.iloc[i] / closes.iloc[i - 1] - 1) for i in range(1, len(closes))]

        # Beta vs SPY
        if spy_returns and len(daily_ret) == len(spy_returns):
            n = len(daily_ret)
            mean_r = sum(daily_ret) / n
            mean_s = sum(spy_returns) / n
            cov = sum((daily_ret[i] - mean_r) * (spy_returns[i] - mean_s) for i in range(n)) / max(n - 1, 1)
            var_s = sum((spy_returns[i] - mean_s) ** 2 for i in range(n)) / max(n - 1, 1)
            beta = round(cov / var_s, 2) if var_s > 0 else None
            if beta is not None:
                betas.append(beta)

        # Weighted daily returns for portfolio Sharpe/drawdown
        weight = abs(mktval) / max(equity, 1)
        for di, r in enumerate(daily_ret):
            pos_returns_by_day[di] = pos_returns_by_day.get(di, 0) + r * weight

    # Portfolio-level returns list
    port_returns = list(pos_returns_by_day.values()) if pos_returns_by_day else []

    sharpe, max_dd = None, None
    if len(port_returns) >= 10:
        n = len(port_returns)
        mean_r = sum(port_returns) / n
        std_r = math.sqrt(sum((r - mean_r) ** 2 for r in port_returns) / max(n - 1, 1))
        sharpe = round((mean_r / std_r) * math.sqrt(252), 2) if std_r > 0 else None

        # Max drawdown on cumulative portfolio curve
        cumulative, peak, max_dd = 1.0, 1.0, 0.0
        for r in port_returns:
            cumulative *= 1 + r
            peak = max(peak, cumulative)
            max_dd = max(max_dd, (peak - cumulative) / peak * 100)
        max_dd = round(-max_dd, 2)

    avg_beta = round(sum(betas) / len(betas), 2) if betas else None

    risk_level = "low"
    if avg_beta is not None and avg_beta > 1.5:
        risk_level = "high"
    elif avg_beta is not None and avg_beta > 1.0:
        risk_level = "medium"
    if sharpe is not None and sharpe < 0:
        risk_level = "high"

    return {
        "positions": len(positions),
        "total_exposure": round(total_exposure, 2),
        "exposure_pct": round(total_exposure / max(equity, 1) * 100, 1),
        "beta": avg_beta,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "risk_level": risk_level,
    }


@router.get("/volatility-target")
async def volatility_target(tickers: str = "", user: User = Depends(get_current_user)):
    """
    Compute correlation-based inverse-vol weights scaled to a 15% annualised
    portfolio volatility target. Pass comma-separated tickers or leave empty
    for the default cross-asset basket (SPY, QQQ, IWM, GLD, TLT, HYG, XLE, XLK, XLF).

    Response includes per-asset weight, individual volatility, and any high-
    correlation pairs (|corr| > 0.70) that received a weight penalty.
    """
    from services.volatility_targeting import get_volatility_target_weights

    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()] if tickers else None
    result = await get_volatility_target_weights(ticker_list)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
