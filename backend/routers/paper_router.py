from config import get_settings
from fastapi import APIRouter, Depends, HTTPException
from models import User
from pydantic import BaseModel
from services import alpaca_rest
from services.auth_svc import get_current_user

router = APIRouter(prefix="/api/paper", tags=["paper"])


def _require_keys():
    s = get_settings()
    if not s.alpaca_api_key or not s.alpaca_api_secret:
        raise HTTPException(403, "Alpaca API keys not configured — set ALPACA_API_KEY and ALPACA_API_SECRET in .env")
    return s.alpaca_api_key, s.alpaca_api_secret.get_secret_value()


def _require_paper_user(user: User):
    if not (user.is_owner or user.subscription_tier == "pro"):
        raise HTTPException(403, "Paper trading requires Pro tier.")


class OrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str  # "buy" | "sell"
    order_type: str = "market"  # "market" | "limit"
    limit_price: float | None = None


@router.get("/account")
async def account(user: User = Depends(get_current_user)):
    key, secret = _require_keys()
    try:
        return await alpaca_rest.get_account(key, secret)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/positions")
async def positions(user: User = Depends(get_current_user)):
    s = get_settings()
    if not s.alpaca_api_key:
        return []
    try:
        return await alpaca_rest.get_positions(s.alpaca_api_key, s.alpaca_api_secret.get_secret_value())
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.get("/orders")
async def orders(status: str = "all", user: User = Depends(get_current_user)):
    s = get_settings()
    if not s.alpaca_api_key:
        return []
    try:
        return await alpaca_rest.get_orders(s.alpaca_api_key, s.alpaca_api_secret.get_secret_value(), status)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.post("/orders")
async def place_order(req: OrderRequest, user: User = Depends(get_current_user)):
    _require_paper_user(user)
    key, secret = _require_keys()
    if req.side not in ("buy", "sell"):
        raise HTTPException(400, "side must be 'buy' or 'sell'")
    if req.qty <= 0:
        raise HTTPException(400, "qty must be positive")
    try:
        return await alpaca_rest.place_order(
            key,
            secret,
            req.symbol,
            req.qty,
            req.side,
            req.order_type,
            req.limit_price,
        )
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.delete("/positions/{symbol}")
async def close_position(symbol: str, user: User = Depends(get_current_user)):
    key, secret = _require_keys()
    try:
        return await alpaca_rest.close_position(key, secret, symbol)
    except Exception as e:
        raise HTTPException(502, "Broker request failed")


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user: User = Depends(get_current_user)):
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
    import math

    from services.alpaca_rest import get_account, get_positions
    from services.market_data import get_histories_batch

    key, secret = _require_keys()
    try:
        positions = await get_positions(key, secret)
        account = await get_account(key, secret)
    except Exception as e:
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
    equity = float(account.get("equity") or 1)
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
