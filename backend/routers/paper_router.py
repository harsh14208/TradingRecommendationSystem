import logging

from config import get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import BrokerOrder, User
from pydantic import BaseModel
from services import alpaca_rest, market_data
from services.auth_svc import get_current_user
from services.broker_svc import _normalize_broker_status
from services.options_paper import options_paper_credentials
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.paper_router")

router = APIRouter(prefix="/api/paper", tags=["paper"])


def _unwrap(secret_val):
    if not secret_val:
        return ""
    if hasattr(secret_val, "get_secret_value"):
        return secret_val.get_secret_value() or ""
    return str(secret_val)


def _num(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _require_keys():
    s = get_settings()
    raw_key = _unwrap(s.alpaca_api_key)
    raw_secret = _unwrap(s.alpaca_api_secret)
    if not raw_key or not raw_secret:
        raise HTTPException(403, "Alpaca API keys not configured — set ALPACA_API_KEY and ALPACA_API_SECRET in .env")
    return raw_key, raw_secret


def _require_se_keys():
    s = get_settings()
    raw_key = _unwrap(s.alpaca_se_api_key)
    raw_secret = _unwrap(s.alpaca_se_api_secret)
    if not raw_key or not raw_secret:
        raise HTTPException(
            403, "COT/signal-engine Alpaca keys not configured — set alpaca_se_api_key and alpaca_se_api_secret in .env"
        )
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
    from sqlalchemy import select

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

    # Live orders from the current Alpaca options paper account, enriched with
    # strategy metadata from our local broker_orders table. Using Alpaca as the
    # source means resetting the options paper account (new account id / wiped
    # orders) automatically clears the history shown here.
    live_orders: list[dict] = []
    creds = options_paper_credentials(settings)
    if creds:
        try:
            key, secret = creds
            raw = await alpaca_rest.get_orders(key, secret, status="all", limit=200)
            live_orders = raw if isinstance(raw, list) else []
        except Exception as exc:
            log.warning("options orders fetch failed: %s", exc)

    # Build lookup of DB records by Alpaca order id so we can attach strategy.
    rows = (
        await db.execute(
            select(BrokerOrder, Signal.option_strategy)
            .outerjoin(Signal, Signal.id == BrokerOrder.signal_id)
            .where(BrokerOrder.broker == "alpaca_options")
        )
    ).all()
    db_by_alpaca_id: dict[str, tuple[BrokerOrder, str | None]] = {}
    for o, strat in rows:
        if o.alpaca_order_id:
            db_by_alpaca_id[o.alpaca_order_id] = (o, strat)

    def _normalize_options_order(raw: dict) -> dict:
        oid = raw.get("id") or raw.get("alpaca_order_id")
        db_rec, strategy = db_by_alpaca_id.get(oid, (None, None))
        status = _normalize_broker_status(raw.get("status"))
        created = raw.get("created_at") or raw.get("submitted_at")
        legs = raw.get("legs") or (db_rec.option_legs if db_rec else None) or []
        symbol = raw.get("symbol") or (db_rec.symbol if db_rec else None) or "—"
        return {
            "id": oid,
            "symbol": symbol,
            "strategy": strategy,
            "side": (raw.get("side") or (db_rec.side if db_rec else "buy")).lower(),
            "status": status,
            "qty": _num(raw.get("qty") or raw.get("filled_qty") or (db_rec.requested_qty if db_rec else 0)),
            "alpaca_order_id": oid,
            "reject_reason": raw.get("reject_reason") or (db_rec.reject_reason if db_rec else None),
            "legs": legs,
            "created_at": created,
        }

    orders = [_normalize_options_order(o) for o in live_orders]
    orders.sort(key=lambda x: x["created_at"] or "", reverse=True)

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


@router.get("/cot/account")
async def cot_account(user: User = Depends(get_current_user)):
    """COT / signal-engine shadow book account (separate Alpaca paper keys)."""
    _require_paper_user(user)
    key, secret = _require_se_keys()
    try:
        return await alpaca_rest.get_account(key, secret)
    except alpaca_rest.AlpacaAuthError as e:
        raise HTTPException(403, f"COT Alpaca keys are invalid or the account is unauthorized: {e}")
    except alpaca_rest.AlpacaRateLimitError as e:
        raise HTTPException(429, f"Alpaca rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/cot/positions")
async def cot_positions(user: User = Depends(get_current_user)):
    """Open positions for the COT / signal-engine shadow book."""
    _require_paper_user(user)
    key, secret = _require_se_keys()
    try:
        return await alpaca_rest.get_positions(key, secret)
    except alpaca_rest.AlpacaAuthError as e:
        raise HTTPException(403, f"COT Alpaca keys are invalid or the account is unauthorized: {e}")
    except alpaca_rest.AlpacaRateLimitError as e:
        raise HTTPException(429, f"Alpaca rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/cot/orders")
async def cot_orders(status: str = "all", user: User = Depends(get_current_user)):
    """Recent orders for the COT / signal-engine shadow book."""
    _require_paper_user(user)
    key, secret = _require_se_keys()
    try:
        return await alpaca_rest.get_orders(key, secret, status)
    except alpaca_rest.AlpacaAuthError as e:
        raise HTTPException(403, f"COT Alpaca keys are invalid or the account is unauthorized: {e}")
    except alpaca_rest.AlpacaRateLimitError as e:
        raise HTTPException(429, f"Alpaca rate limit exceeded: {e}")
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/cot/risk")
async def cot_portfolio_risk(user: User = Depends(get_current_user)):
    """
    Aggregate risk metrics across the COT / signal-engine shadow book.
    Uses the same methodology as the equity risk endpoint.
    """
    _require_paper_user(user)
    from services.alpaca_rest import get_account, get_positions
    from services.portfolio_risk import compute_portfolio_risk

    key, secret = _require_se_keys()
    account_error = None
    auth_error = None
    try:
        positions = await get_positions(key, secret)
    except alpaca_rest.AlpacaAuthError as e:
        auth_error = str(e)
        positions = []
    except Exception as e:
        positions = []
        account_error = str(e)
    try:
        account = await get_account(key, secret)
    except alpaca_rest.AlpacaAuthError as e:
        auth_error = auth_error or str(e)
        account = None
    except Exception as e:
        account = None
        account_error = account_error or str(e)

    if auth_error:
        raise HTTPException(403, f"COT Alpaca keys are invalid or the account is unauthorized: {auth_error}")
    if account_error and not positions and not account:
        raise HTTPException(502, "Broker request failed")

    equity = float(account.get("equity") or 1) if account else 1.0
    return await compute_portfolio_risk(
        positions or [], equity, api_key=key, api_secret=secret, benchmark="SPY", period="1y", interval="1d"
    )


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

    # Margin-free guard: trade only with non-margin buying power and never open a
    # naked short position. This keeps the paper book cash-secured.
    account = None
    try:
        account = await alpaca_rest.get_account(key, secret)
    except Exception as exc:
        log.warning("paper order: account check failed: %s", exc)
        raise HTTPException(502, "Broker account check failed")

    non_margin_bp = float(account.get("non_marginable_buying_power") or account.get("cash") or 0.0)

    if req.side == "buy":
        price = req.limit_price
        if not price:
            quote = await market_data.get_quote(req.symbol)
            price = (quote or {}).get("p") or (quote or {}).get("price") or 0.0
        if not price:
            raise HTTPException(502, "Could not fetch current price for order check")
        estimated_notional = req.qty * price
        if non_margin_bp > 0 and estimated_notional > non_margin_bp:
            raise HTTPException(
                400,
                f"Order notional ${estimated_notional:,.2f} exceeds non-margin buying power ${non_margin_bp:,.2f}",
            )
    else:  # sell
        positions = []
        try:
            positions = await alpaca_rest.get_positions(key, secret)
        except Exception as exc:
            log.warning("paper order: positions fetch failed: %s", exc)
        long_qty = 0.0
        for pos in positions:
            if (pos.get("symbol") or "").upper() == req.symbol.upper() and (pos.get("side") or "").lower() == "long":
                long_qty = float(pos.get("qty") or 0.0)
                break
        if req.qty > long_qty:
            raise HTTPException(
                400,
                f"Sell qty {req.qty} exceeds long position {long_qty:.0f}; naked short selling is disabled",
            )

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
    Aggregate risk metrics across all open equity paper positions:
    Sharpe ratio, max drawdown, beta vs SPY, total exposure.
    """
    _require_paper_user(user)
    from services.alpaca_rest import get_account, get_positions
    from services.portfolio_risk import compute_portfolio_risk

    key, secret = _require_keys()
    account_error = None
    try:
        positions = await get_positions(key, secret)
    except Exception as e:
        positions = []
        account_error = str(e)
    try:
        account = await get_account(key, secret)
    except Exception as e:
        account = None
        account_error = account_error or str(e)

    if account_error and not positions and not account:
        raise HTTPException(502, "Broker request failed")

    equity = float(account.get("equity") or 1) if account else 1.0
    return await compute_portfolio_risk(
        positions or [], equity, api_key=key, api_secret=secret, benchmark="SPY", period="1y", interval="1d"
    )


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
