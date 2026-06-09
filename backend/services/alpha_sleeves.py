"""
services/alpha_sleeves.py

QENG-5a: PCA/ETF residual stat-arb sleeve (Avellaneda-Lee style residual reversion).
QENG-5b: Time-series momentum / crisis trend sleeve (macro asset classes).
QENG-5c: Lower-turnover cross-sectional factor sleeve.
QENG-5d: Cross-sleeve capital allocator (Sharpe-based capital allocation).
"""

import logging
import math
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Signal

from services.market_data import get_histories_batch

log = logging.getLogger("signal.trade.alpha_sleeves")

# Asset list for time-series momentum trend sleeve
TREND_ETFS = ["SPY", "QQQ", "TLT", "GLD", "DXY", "HYG"]


async def compute_etf_residual_stat_arb(
    tickers: list[str], sector_etfs: dict[str, str], lookback_days: int = 60
) -> dict[str, dict[str, float]]:
    """
    QENG-5a: PCA/ETF residual stat-arb sleeve.
    Regresses each ticker on its sector ETF and calculates the residual z-score.
    BUY when z-score < -2.0, SELL when z-score > 2.0.
    """
    results = {}
    if not tickers:
        return results

    unique_etfs = list(set(sector_etfs.values()))
    all_needed = list(set(tickers + unique_etfs))

    try:
        histories = await get_histories_batch(all_needed, period="6mo", interval="1d")

        for t in tickers:
            etf = sector_etfs.get(t)
            if not etf or t not in histories or etf not in histories:
                continue

            df_stock = histories[t]
            df_etf = histories[etf]

            if len(df_stock) < lookback_days or len(df_etf) < lookback_days:
                continue

            close_s = df_stock["Close"].astype(float).values[-lookback_days:]
            close_e = df_etf["Close"].astype(float).values[-lookback_days:]

            # Daily returns
            ret_s = np.diff(close_s) / close_s[:-1]
            ret_e = np.diff(close_e) / close_e[:-1]

            # Regress stock returns on ETF returns (OLS)
            # R_s = alpha + beta * R_e + epsilon
            A = np.column_stack([np.ones_like(ret_e), ret_e])
            beta_vector, residuals, _, _ = np.linalg.lstsq(A, ret_s, rcond=None)

            alpha, beta = beta_vector[0], beta_vector[1]

            # Current residual
            last_ret_s = ret_s[-1]
            last_ret_e = ret_e[-1]
            last_residual = last_ret_s - (alpha + beta * last_ret_e)

            # Historical residuals for standardisation
            all_residuals = ret_s - (alpha + beta * ret_e)
            mean_res = np.mean(all_residuals)
            std_res = np.std(all_residuals)
            std_res = max(std_res, 0.0001)

            # Residual z-score
            z_score = (last_residual - mean_res) / std_res

            # Ornstein-Uhlenbeck (OU) parameter estimation (for half-life filter)
            # X_t = a * X_{t-1} + b + e
            X_t = all_residuals[1:]
            X_tm1 = all_residuals[:-1]

            A_ou = np.column_stack([np.ones_like(X_tm1), X_tm1])
            beta_ou, _, _, _ = np.linalg.lstsq(A_ou, X_t, rcond=None)

            a_param = beta_ou[1]
            # OU half-life = -ln(2) / ln(a)
            if 0 < a_param < 1.0:
                half_life = -np.log(2.0) / np.log(a_param)
            else:
                half_life = 99.0  # fallback for non-stationary/non-reverting

            action = "HOLD"
            if z_score < -2.0 and half_life < 25.0:
                action = "BUY"
            elif z_score > 2.0 and half_life < 25.0:
                action = "SELL"

            results[t] = {
                "z_score": float(z_score),
                "beta": float(beta),
                "half_life": float(half_life),
                "action": action,
            }
    except Exception as e:
        log.error(f"Failed to calculate residual stat-arb: {e}", exc_info=True)

    return results


async def compute_time_series_momentum() -> dict[str, str]:
    """
    QENG-5b: Time-series momentum / crisis trend sleeve.
    Checks SPY, QQQ, TLT, GLD, DXY, HYG price relative to 200-day moving average.
    Returns: {etf: "bull" | "bear"}
    """
    results = {}
    try:
        histories = await get_histories_batch(TREND_ETFS, period="1y", interval="1d")
        for etf in TREND_ETFS:
            df = histories.get(etf)
            if df is None or len(df) < 200:
                continue
            close = df["Close"].astype(float).values
            current_price = close[-1]
            sma_200 = np.mean(close[-200:])

            results[etf] = "bull" if current_price > sma_200 else "bear"
    except Exception as e:
        log.error(f"Failed to compute TS momentum: {e}", exc_info=True)
    return results


async def compute_cross_sectional_factor_scores(tickers: list[str]) -> dict[str, float]:
    """
    QENG-5c: Lower-turnover cross-sectional factor sleeve.
    Scores tickers based on a blend of Value (trailing 60d return - reverse momentum),
    Quality (lower volatility), and Momentum (120d return).
    """
    scores = {}
    if not tickers:
        return scores

    try:
        histories = await get_histories_batch(tickers, period="1y", interval="1d")

        mom_120d = {}
        vol_60d = {}
        rev_mom_60d = {}

        for t in tickers:
            df = histories.get(t)
            if df is None or len(df) < 120:
                continue
            close = df["Close"].astype(float).values

            # Momentum (120d price return)
            mom_120d[t] = (close[-1] - close[-120]) / close[-120]

            # Volatility (60d return standard deviation)
            rets_60 = np.diff(close[-60:]) / close[-60:-1]
            vol_60d[t] = np.std(rets_60)

            # Value / Reverse momentum (negative of 60d return)
            rev_mom_60d[t] = -((close[-1] - close[-60]) / close[-60])

        # Rank features cross-sectionally
        def rank_dict(d: dict, reverse: bool = False) -> dict:
            sorted_keys = sorted(d, key=d.get, reverse=reverse)
            return {k: i / len(d) for i, k in enumerate(sorted_keys)}

        rank_mom = rank_dict(mom_120d)
        rank_vol = rank_dict(vol_60d, reverse=True)  # lower volatility is better (higher rank)
        rank_rev = rank_dict(rev_mom_60d)

        for t in mom_120d:
            # Equal-weighted factor score
            scores[t] = float(0.4 * rank_mom[t] + 0.3 * rank_vol[t] + 0.3 * rank_rev[t])

    except Exception as e:
        log.error(f"Failed to calculate cross-sectional factor scores: {e}", exc_info=True)

    return scores


async def get_dynamic_sleeve_sharpes(db: AsyncSession, lookback_days: int = 30) -> dict[str, float]:
    """
    REF-3: Calculate rolling out-of-sample Sharpe ratios for each sleeve.
    Uses historical database signals for MR, and simulates simple daily returns
    for StatArb, Trend, and Factor sleeves over the lookback window.
    """
    sharpes = {"MR": 1.0, "StatArb": 1.0, "Trend": 1.0, "Factor": 1.0}
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)

    # 1. MR Sharpe (using resolved live signals)
    try:
        stmt = select(Signal.outcome_pct).where(Signal.outcome_pct.isnot(None), Signal.created_at >= cutoff)
        res = await db.execute(stmt)
        rets = [float(r) for (r,) in res.all() if r is not None]
        if len(rets) >= 5:
            mean = np.mean(rets)
            std = np.std(rets)
            if std > 0.0001:
                # Annualise simple return (assumes ~10d holding period, so 25 periods per year)
                sharpes["MR"] = max(0.1, (mean / std) * math.sqrt(25.0))
    except Exception as e:
        log.warning(f"Failed to calculate dynamic MR Sharpe: {e}")

    # 2. Trend Sharpe (simulated trend-following on TREND_ETFS)
    try:
        histories = await get_histories_batch(TREND_ETFS, period="1y", interval="1d")
        trend_daily_rets = []
        for etf in TREND_ETFS:
            df = histories.get(etf)
            if df is not None and len(df) >= 200:
                closes = df["Close"].astype(float).values[-lookback_days - 1 :]
                smas = [
                    np.mean(df["Close"].astype(float).values[i - 200 : i])
                    for i in range(len(df) - lookback_days, len(df))
                ]
                # Daily strategy returns
                for idx in range(1, len(closes)):
                    day_ret = (closes[idx] - closes[idx - 1]) / closes[idx - 1]
                    if closes[idx - 1] > smas[idx - 1]:
                        trend_daily_rets.append(day_ret)
                    else:
                        trend_daily_rets.append(0.0)  # flat
        if len(trend_daily_rets) >= 10:
            mean = np.mean(trend_daily_rets)
            std = np.std(trend_daily_rets)
            if std > 0.0001:
                sharpes["Trend"] = max(0.1, (mean / std) * math.sqrt(252.0))
    except Exception as e:
        log.warning(f"Failed to calculate dynamic Trend Sharpe: {e}")

    # 3. StatArb Sharpe (simulated AAPL/MSFT stat-arb returns)
    try:
        tickers = ["AAPL", "MSFT"]
        sector_etfs = {"AAPL": "XLK", "MSFT": "XLK"}
        histories = await get_histories_batch(["AAPL", "MSFT", "XLK"], period="6mo", interval="1d")

        arb_daily_rets = []
        for t in tickers:
            df_stock = histories.get(t)
            df_etf = histories.get("XLK")
            if df_stock is not None and df_etf is not None and len(df_stock) >= 60:
                closes_s = df_stock["Close"].astype(float).values
                closes_e = df_etf["Close"].astype(float).values

                # Regress and trace daily residual
                for idx in range(len(closes_s) - lookback_days, len(closes_s)):
                    window_s = closes_s[idx - 60 : idx]
                    window_e = closes_e[idx - 60 : idx]

                    ret_s = np.diff(window_s) / window_s[:-1]
                    ret_e = np.diff(window_e) / window_e[:-1]

                    A = np.column_stack([np.ones_like(ret_e), ret_e])
                    beta_vector, residuals, _, _ = np.linalg.lstsq(A, ret_s, rcond=None)
                    alpha, beta = beta_vector[0], beta_vector[1]

                    all_residuals = ret_s - (alpha + beta * ret_e)
                    mean_res = np.mean(all_residuals)
                    std_res = max(np.std(all_residuals), 0.0001)

                    # Next day return
                    next_ret_s = (closes_s[idx] - closes_s[idx - 1]) / closes_s[idx - 1]
                    next_ret_e = (closes_e[idx] - closes_e[idx - 1]) / closes_e[idx - 1]
                    next_res = next_ret_s - (alpha + beta * next_ret_e)
                    z = (next_res - mean_res) / std_res

                    # If z was low yesterday, go long stock / short ETF
                    if z < -2.0:
                        arb_daily_rets.append(next_ret_s - beta * next_ret_e)
                    elif z > 2.0:
                        arb_daily_rets.append(-(next_ret_s - beta * next_ret_e))
                    else:
                        arb_daily_rets.append(0.0)

        if len(arb_daily_rets) >= 10:
            mean = np.mean(arb_daily_rets)
            std = np.std(arb_daily_rets)
            if std > 0.0001:
                sharpes["StatArb"] = max(0.1, (mean / std) * math.sqrt(252.0))
    except Exception as e:
        log.warning(f"Failed to calculate dynamic StatArb Sharpe: {e}")

    # 4. Factor Sharpe (simulated factor long-short returns)
    try:
        tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOG"]
        histories = await get_histories_batch(tickers, period="6mo", interval="1d")

        factor_daily_rets = []
        for idx in range(120, min(120 + lookback_days, len(histories["AAPL"]))):
            daily_scores = {}
            daily_rets = {}
            for t in tickers:
                df = histories.get(t)
                if df is not None and len(df) > idx:
                    close = df["Close"].astype(float).values[:idx]
                    mom = (close[-1] - close[-120]) / close[-120]
                    rets_60 = np.diff(close[-60:]) / close[-60:-1]
                    vol = np.std(rets_60)
                    daily_scores[t] = mom - vol
                    next_close = df["Close"].astype(float).values[idx]
                    daily_rets[t] = (next_close - close[-1]) / close[-1]
            if daily_scores:
                sorted_t = sorted(daily_scores, key=daily_scores.get)
                long_t = sorted_t[-1]
                short_t = sorted_t[0]
                factor_daily_rets.append(daily_rets[long_t] - daily_rets[short_t])

        if len(factor_daily_rets) >= 5:
            mean = np.mean(factor_daily_rets)
            std = np.std(factor_daily_rets)
            if std > 0.0001:
                sharpes["Factor"] = max(0.1, (mean / std) * math.sqrt(252.0))
    except Exception as e:
        log.warning(f"Failed to calculate dynamic Factor Sharpe: {e}")

    # 2026-06-08 standalone validation (scripts/backtest_sleeves.py, 23yr IS): the
    # non-MR sleeves do NOT carry deployable alpha and must not draw capital on the
    # toy/rolling estimates above —
    #   • StatArb: non-viable on this universe (cumulative-spread gross edge < 2-leg
    #     friction; the live daily-return formulation also churns at a 1-day half-life);
    #   • Trend: apparent Sharpe is multi-asset *basket beta* (buy-hold beats the SMA
    #     timing) inflated by the 2003-21 bond bull — not repeatable timing alpha;
    #   • Factor: never validated.
    # Force them to 0.0 so allocate_cross_sleeve_capital concentrates on the only
    # validated sleeve (MR). Re-enable a sleeve only after a standalone + correlation
    # backtest proves a positive, MR-diversifying edge.
    for _unvalidated in ("StatArb", "Trend", "Factor"):
        sharpes[_unvalidated] = 0.0
    log.info(f"Dynamic cross-sleeve Sharpe ratios (non-MR sleeves disabled pending validation): {sharpes}")
    return sharpes


def allocate_cross_sleeve_capital(sleeve_sharpes: dict[str, float], total_capital: float) -> dict[str, float]:
    """
    QENG-5d: Cross-sleeve capital allocator.
    Allocates capital proportional to positive Sharpe, capping each ACTIVE sleeve
    between 10% and 50%. Sleeves with Sharpe <= 0 (disabled/money-losing — e.g. the
    non-MR sleeves pending re-validation) receive 0 and are NOT floored to 10% (the
    old behaviour funded validated money-losers). Falls back to equal weight only if
    no sleeve is active.
    """
    active = {name: sh for name, sh in sleeve_sharpes.items() if sh > 0}
    if not active:
        n = max(len(sleeve_sharpes), 1)
        return {name: total_capital / n for name in sleeve_sharpes}
    adjusted = dict(active)

    total_adj = sum(adjusted.values())
    raw_alloc = {name: (val / total_adj) * total_capital for name, val in adjusted.items()}

    # Enforce min 10% and max 50% capital allocation constraints per sleeve
    min_alloc = 0.10 * total_capital
    max_alloc = 0.50 * total_capital

    final_alloc = {name: 0.0 for name in sleeve_sharpes}  # disabled sleeves stay at 0
    remaining_capital = total_capital
    unconstrained = list(raw_alloc.keys())

    # Apply floor
    for name in list(unconstrained):
        if raw_alloc[name] < min_alloc:
            final_alloc[name] = min_alloc
            remaining_capital -= min_alloc
            unconstrained.remove(name)

    # Apply ceiling
    for name in list(unconstrained):
        if raw_alloc[name] > max_alloc:
            final_alloc[name] = max_alloc
            remaining_capital -= max_alloc
            unconstrained.remove(name)

    # Distribute remainder to unconstrained sleeves
    if unconstrained:
        curr_total = sum(adjusted[name] for name in unconstrained)
        for name in unconstrained:
            final_alloc[name] = (adjusted[name] / curr_total) * remaining_capital
    else:
        # Fallback if all sleeves hit constraints
        for name in raw_alloc:
            final_alloc[name] = total_capital / len(raw_alloc)

    return final_alloc
