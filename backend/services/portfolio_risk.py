"""Portfolio-level historical risk metrics.

Computes beta vs a benchmark from current holdings and Sharpe / max drawdown from
the account's actual portfolio history (Alpaca ``/v2/account/portfolio/history``),
so both open and closed P&L are included since trading started.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from config import get_settings
from services.market_data import get_histories_batch

log = logging.getLogger("signal.portfolio_risk")


def _num(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _signed_market_value(qty: float, market_value: float) -> float:
    """Return a signed market value: negative for short positions."""
    if qty < 0:
        return -abs(_num(market_value))
    return _num(market_value)


def _daily_returns(df: pd.DataFrame) -> pd.Series:
    """Close-to-close daily returns indexed by date."""
    closes = df["Close"].astype(float)
    return closes.pct_change().dropna()


def _history_sharpe_maxdd(equity_values: pd.Series, risk_free_rate: float = 0.0) -> tuple[float | None, float | None]:
    """Annualised Sharpe and max drawdown from an equity time series.

    Sharpe is computed on *excess* daily returns over the configured annual
    risk-free rate, which is the standard definition. Without this adjustment,
    a near-cash account with very low volatility can show a misleadingly high
    Sharpe even when it barely beats Treasury bills.
    """
    returns = equity_values.pct_change().dropna()
    if len(returns) < 2:
        return None, None

    # Convert annual risk-free rate to a daily compounded rate.
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
    excess = returns - daily_rf

    mean_ex = excess.mean()
    std_ex = excess.std()
    sharpe = round((mean_ex / std_ex) * np.sqrt(252), 2) if std_ex and std_ex > 0 else None

    cumulative = equity_values / equity_values.iloc[0]
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak) / peak
    max_dd = round(drawdown.min() * 100, 2) if not drawdown.empty else None
    return sharpe, max_dd


async def _fetch_account_history_sharpe(
    api_key: str | None,
    api_secret: str | None,
    risk_free_rate: float = 0.0,
) -> tuple[float | None, float | None, int]:
    """Return (sharpe, max_drawdown, n_obs) from Alpaca portfolio history."""
    if not api_key or not api_secret:
        return None, None, 0
    try:
        from services import alpaca_rest

        hist = await alpaca_rest.get_portfolio_history(api_key, api_secret, period="1A", timeframe="1D")
        equity = hist.get("equity") or hist.get("profit_loss")
        if not equity:
            return None, None, 0
        series = pd.Series([_num(v) for v in equity if v is not None]).replace(0, np.nan).dropna()
        if len(series) < 2:
            return None, None, 0
        sharpe, max_dd = _history_sharpe_maxdd(series, risk_free_rate=risk_free_rate)
        return sharpe, max_dd, len(series)
    except Exception as exc:
        log.warning("portfolio history fetch failed: %s", exc)
        return None, None, 0


def _per_trade_sharpe(positions: list[dict[str, Any]]) -> float | None:
    """Fallback Sharpe using only currently open positions' unrealised returns."""
    trade_returns: list[float] = []
    for p in positions:
        cost = _num(p.get("cost_basis"))
        upl = _num(p.get("unrealized_pl"))
        if abs(cost) > 0:
            trade_returns.append(upl / abs(cost))
    if len(trade_returns) < 2:
        return None
    mean_tr = np.mean(trade_returns)
    std_tr = np.std(trade_returns, ddof=1)
    return round(mean_tr / std_tr, 2) if std_tr and std_tr > 0 else None


async def compute_portfolio_risk(
    positions: list[dict[str, Any]],
    equity: float,
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    benchmark: str = "SPY",
    period: str = "1y",
    interval: str = "1d",
    min_observations: int = 30,
) -> dict[str, Any]:
    """Return risk metrics for an equity/ETF paper book.

    Beta is computed from current positions and benchmark price histories.
    Sharpe and max drawdown come from the Alpaca portfolio-history endpoint when
    credentials are supplied, so they reflect both open and closed P&L since the
    account started trading. If portfolio history is unavailable, Sharpe falls
    back to the open-position per-trade estimate.

    Args:
        positions: list of dicts with at least ``symbol``, ``qty``, and
            ``market_value`` keys (Alpaca position shape).
        equity: total account equity used to normalise exposure.
        api_key/api_secret: Alpaca credentials used to fetch portfolio history.
        benchmark: ticker to compute beta against (default SPY).
        period: price-history period passed to ``get_histories_batch``.
        interval: price-history interval passed to ``get_histories_batch``.
        min_observations: minimum number of overlapping daily returns needed
            to report beta.

    Returns:
        dict with ``positions``, ``total_exposure``, ``exposure_pct``,
        ``benchmark``, ``beta``, ``sharpe``, ``max_drawdown``, ``risk_level``,
        ``history_observations`` and ``proxy``.
    """
    # Clean position list and compute exposure.
    clean_positions: list[dict[str, Any]] = []
    total_exposure = 0.0
    for p in positions:
        sym = (p.get("symbol") or "").upper()
        if not sym:
            continue
        qty = _num(p.get("qty"))
        mv = _num(p.get("market_value"))
        signed_mv = _signed_market_value(qty, mv)
        total_exposure += abs(signed_mv)
        clean_positions.append({"symbol": sym, "qty": qty, "signed_mv": signed_mv, "abs_mv": abs(signed_mv)})

    # ── Sharpe / max drawdown from account history (open + closed trades) ─────
    sharpe, max_dd, hist_obs, proxy = None, None, 0, "none"
    settings = get_settings()
    risk_free_rate = float(getattr(settings, "risk_free_rate", 0.0))
    if api_key and api_secret:
        sharpe, max_dd, hist_obs = await _fetch_account_history_sharpe(
            api_key, api_secret, risk_free_rate=risk_free_rate
        )
        if hist_obs:
            proxy = "account_history"
    if sharpe is None:
        sharpe = _per_trade_sharpe(positions)
        if sharpe is not None:
            proxy = "open_positions"

    # ── Beta from current holdings vs benchmark ───────────────────────────────
    beta = None
    observations = 0
    if clean_positions:
        tickers = [p["symbol"] for p in clean_positions] + [benchmark]
        histories = await get_histories_batch(tickers, period=period, interval=interval)
        benchmark_series = _daily_returns(histories.get(benchmark, pd.DataFrame()))

        if not benchmark_series.empty:
            weighted_returns: list[pd.Series] = []
            betas: list[float] = []
            for p in clean_positions:
                sym = p["symbol"]
                df = histories.get(sym)
                if df is None or df.empty or len(df) < 2:
                    continue
                sym_returns = _daily_returns(df)
                if sym_returns.empty:
                    continue

                # Direction: long positions contribute +return, short positions -return.
                direction = -1.0 if p["qty"] < 0 else 1.0
                weight = p["abs_mv"] / max(equity, 1.0)
                weighted_returns.append(sym_returns * direction * weight)

                aligned = pd.concat([sym_returns, benchmark_series], axis=1).dropna()
                if len(aligned) >= min_observations:
                    bench_var = aligned.iloc[:, 1].var()
                    if bench_var and bench_var > 0:
                        betas.append(aligned.iloc[:, 0].cov(aligned.iloc[:, 1]) / bench_var)

            if weighted_returns:
                portfolio_returns = pd.concat(weighted_returns, axis=1).sum(axis=1, skipna=True).dropna()
                aligned = pd.concat([portfolio_returns, benchmark_series], axis=1).dropna()
                aligned.columns = ["portfolio", "benchmark"]
                observations = len(aligned)
                if observations >= min_observations:
                    bench_var = aligned["benchmark"].var()
                    if bench_var and bench_var > 0:
                        beta = round(aligned["portfolio"].cov(aligned["benchmark"]) / bench_var, 2)
            if beta is None and betas:
                beta = round(sum(betas) / len(betas), 2)

    if not clean_positions:
        risk_level = "none"
    else:
        risk_level = "low"
        if beta is not None and beta > 1.5:
            risk_level = "high"
        elif beta is not None and beta > 1.0:
            risk_level = "medium"
        if sharpe is not None and sharpe < 0:
            risk_level = "high"

    return {
        "positions": len(clean_positions),
        "total_exposure": round(total_exposure, 2),
        "exposure_pct": round(total_exposure / max(equity, 1.0) * 100.0, 1),
        "benchmark": benchmark,
        "beta": beta,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "risk_level": risk_level,
        "history_observations": hist_obs,
        "proxy": proxy,
    }
