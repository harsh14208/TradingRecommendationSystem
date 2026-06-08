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
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Instrument, Position
from services.market_data import get_histories_batch

log = logging.getLogger("signal.trade.alpha_sleeves")

# Asset list for time-series momentum trend sleeve
TREND_ETFS = ["SPY", "QQQ", "TLT", "GLD", "DXY", "HYG"]

async def compute_etf_residual_stat_arb(
    tickers: List[str],
    sector_etfs: Dict[str, str],
    lookback_days: int = 60
) -> Dict[str, Dict[str, float]]:
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
                "action": action
            }
    except Exception as e:
        log.error(f"Failed to calculate residual stat-arb: {e}", exc_info=True)
        
    return results

async def compute_time_series_momentum() -> Dict[str, str]:
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

async def compute_cross_sectional_factor_scores(tickers: List[str]) -> Dict[str, float]:
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

def allocate_cross_sleeve_capital(
    sleeve_sharpes: Dict[str, float],
    total_capital: float
) -> Dict[str, float]:
    """
    QENG-5d: Cross-sleeve capital allocator.
    Allocates capital across sleeves (MR, StatArb, Trend, Factor) proportional to their
    positive Sharpe confidence, capping each sleeve between 10% and 50% exposure.
    """
    # Keep Sharpe positive for weights
    adjusted = {}
    for name, sh in sleeve_sharpes.items():
        adjusted[name] = max(sh, 0.1)  # floor at 0.1
        
    total_adj = sum(adjusted.values())
    raw_alloc = {name: (val / total_adj) * total_capital for name, val in adjusted.items()}
    
    # Enforce min 10% and max 50% capital allocation constraints per sleeve
    min_alloc = 0.10 * total_capital
    max_alloc = 0.50 * total_capital
    
    final_alloc = {}
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
