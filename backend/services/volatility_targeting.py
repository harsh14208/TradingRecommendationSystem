"""
Cross-Asset Volatility Targeting

Computes correlation-based portfolio allocation weights to maintain a
constant portfolio-level annualised volatility target (default 15%).

Algorithm:
  1. Fetch 3-month daily returns for all open positions + major asset classes
  2. Build the correlation matrix
  3. Use inverse-volatility weighting as starting point
  4. Apply correlation penalty: pairs with |corr| > 0.7 get their average
     weight reduced proportionally
  5. Rescale to 100% total weight
  6. Return per-asset weight, individual vol, pair correlations above threshold
"""

import asyncio
import logging
from typing import Optional

import numpy as np
import pandas as pd

log = logging.getLogger("signal.trade.vol_target")

TARGET_VOL = 0.15  # 15% annualised portfolio vol target
CORR_THRESHOLD = 0.70  # pairs above this get correlation penalty
TRADING_DAYS = 252


async def _fetch_returns(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    try:
        histories = await get_histories_batch(tickers, period=period, interval="1d")
    except Exception as e:
        log.warning("[vol_target] market data unavailable: %s", e)
        return pd.DataFrame()

    if histories is None:
        return pd.DataFrame()

    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


def _vol_target_weights(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    # Drop columns that are all-NaN or have zero variance to keep linear-algebra stable.
    returns_df = returns_df.dropna(axis=1, how="all").copy()
    returns_df = returns_df.loc[:, returns_df.std() > 1e-12]
    tickers = list(returns_df.columns)
    if len(tickers) < 1:
        return {"error": "No usable return series after removing NaN/zero-variance columns"}

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 1.0
    raw_weights = {t: inv_vols[t] / total_inv for t in tickers}

    # Correlation matrix
    corr_matrix = returns_df.corr()

    # Collect high-correlation pairs and apply penalty
    high_corr_pairs = []
    penalty = {t: 0.0 for t in tickers}

    for i, a in enumerate(tickers):
        for b in tickers[i + 1 :]:
            c = corr_matrix.loc[a, b] if (a in corr_matrix.index and b in corr_matrix.columns) else 0.0
            if abs(c) > CORR_THRESHOLD:
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(float(c), 3)})
                # Penalty proportional to excess correlation
                excess = (abs(c) - CORR_THRESHOLD) / (1.0 - CORR_THRESHOLD)
                penalty[a] += excess * 0.5
                penalty[b] += excess * 0.5

    # Apply penalty: reduce weight by up to 40% for maximally correlated pairs
    penalised_weights = {t: raw_weights[t] * max(0.6, 1.0 - penalty[t]) for t in tickers}
    total_pen = sum(penalised_weights.values()) or 1.0
    final_weights = {t: penalised_weights[t] / total_pen for t in tickers}

    # Estimate portfolio volatility with final weights
    w = np.array([final_weights[t] for t in tickers])
    cov = returns_df.cov() * TRADING_DAYS
    port_var = float(w @ cov.values @ w)
    port_vol = float(np.sqrt(max(port_var, 0)))

    # Scale weights to hit TARGET_VOL (leverage up/down)
    scale_factor = TARGET_VOL / port_vol if port_vol > 1e-6 else 1.0
    # Cap scale at 2x to prevent excessive leverage
    scale_factor = min(scale_factor, 2.0)
    scaled_weights = {t: min(final_weights[t] * scale_factor, 0.40) for t in tickers}

    # Final re-normalise after cap
    total_scaled = sum(scaled_weights.values()) or 1.0
    final = {t: round(scaled_weights[t] / total_scaled, 4) for t in tickers}

    # Sort by weight desc
    sorted_assets = sorted(final.items(), key=lambda x: x[1], reverse=True)

    return {
        "target_vol_pct": round(TARGET_VOL * 100, 1),
        "estimated_port_vol_pct": round(port_vol * 100, 2),
        "scale_factor": round(scale_factor, 3),
        "assets": [
            {
                "ticker": t,
                "weight_pct": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


async def get_volatility_target_weights(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty or len(returns_df.columns) < 2 or len(returns_df) < 10:
            return {"error": "Could not fetch enough return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        # Data-provider hiccups are expected; keep them out of Sentry as errors.
        log.warning(f"[vol_target] Error computing weights: {e}")
        log.debug("[vol_target] traceback", exc_info=True)
        return {"error": str(e)}
