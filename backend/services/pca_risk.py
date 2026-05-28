"""
PCA-Based Portfolio Risk Model

Replaces static sector-bucket limits with 2-factor principal component analysis
on the paper portfolio's current positions. Identifies latent risk factors
("Growth/Value" and "Interest Rate Sensitivity") and flags when the portfolio
is over-exposed to a statistical factor even when sector limits look fine.

Example: NVDA + AMD + TSM all in different GICS sub-sectors but all load heavily
on the "AI Semiconductor" factor. PCA catches this; per-sector limits don't.

Returns:
  factor_exposures: list of {factor, loading, interpretation}
  concentration_warning: bool
  dominant_factor: str
  max_loading: float   — 0 to 1; >0.5 = concentrated
  haircut_pct:  float  — 0–25%; confidence reduction for new BUYs in this cluster

Requires: positions as {ticker: market_value} dict.
Corr matrix computed from last-60d daily returns of the position tickers.
Falls back gracefully if fewer than 3 positions or price data unavailable.
"""

import logging

import numpy as np

log = logging.getLogger("signal.trade.pca_risk")

# Tickers that load heavily on each latent factor (manually curated seeds)
# Used to NAME the factor once PCA identifies the top eigenvector.
_FACTOR_SEEDS: dict[str, list[str]] = {
    "AI / Semiconductor": ["NVDA", "AMD", "TSM", "AMAT", "KLAC", "ARM", "MU", "AVGO"],
    "Interest Rate": ["TLT", "BND", "USB", "JPM", "BAC", "WFC", "C", "PNC"],
    "Energy / Commodity": ["XOM", "CVX", "SLB", "FCX", "SCCO", "GLD", "GDX", "XLE"],
    "Growth / Momentum": ["TSLA", "PLTR", "SNOW", "DDOG", "NET", "CRWD", "MDB", "MSTR"],
    "Defensive / Income": ["KO", "PEP", "JNJ", "PG", "T", "VZ", "SO", "XLU"],
}


def _name_factor(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


async def compute_pca_risk(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = [t for t, v in positions.items() if v > 0]
    if len(tickers) < 3:
        return {}

    # Fetch last lookback_days of daily returns for all position tickers
    try:
        from services.market_data import get_histories_batch

        histories = await get_histories_batch(tickers, period="3mo", interval="1d")
    except Exception as e:
        log.debug(f"[pca_risk] data fetch failed: {e}")
        return {}

    # Build returns matrix: (days × tickers), only tickers with enough data
    returns_cols: dict[str, np.ndarray] = {}
    min_rows = max(lookback_days // 2, 20)
    for t in tickers:
        df = histories.get(t)
        if df is None or len(df) < min_rows:
            continue
        closes = df["Close"].astype(float).values[-lookback_days:]
        rets = np.diff(closes) / closes[:-1]
        returns_cols[t] = rets

    if len(returns_cols) < 3:
        return {}

    # Align lengths (different tickers may have different trading day counts)
    min_len = min(len(v) for v in returns_cols.values())
    R = np.column_stack([v[-min_len:] for v in returns_cols.values()])
    col_tickers = list(returns_cols.keys())

    # Standardise columns (zero mean, unit variance)
    R -= R.mean(axis=0)
    stds = R.std(axis=0)
    stds[stds == 0] = 1.0
    R /= stds

    # Correlation matrix → eigendecomposition
    corr = np.corrcoef(R.T)
    eigvals, eigvecs = np.linalg.eigh(corr)
    # eigh returns ascending order; reverse for descending
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    total_var = eigvals.sum()
    factor_results = []

    for fi in range(min(2, len(eigvals))):
        loadings = eigvecs[:, fi]
        variance_pct = round(eigvals[fi] / total_var * 100, 1)
        # Pair each ticker with its loading on this factor
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=lambda x: -abs(x[1]))
        factor_name = _name_factor(ticker_loads)
        max_load = float(abs(loadings).max())

        # Portfolio exposure to this factor = weighted sum of loadings
        total_mv = sum(positions.get(t, 0) for t in col_tickers)
        port_exposure = 0.0
        if total_mv > 0:
            for t, load in zip(col_tickers, loadings):
                port_exposure += (positions.get(t, 0) / total_mv) * abs(load)

        factor_results.append(
            {
                "factor": factor_name,
                "factor_num": fi + 1,
                "variance_pct": variance_pct,
                "max_loading": round(max_load, 3),
                "port_exposure": round(port_exposure, 3),
                "top_tickers": [t for t, _ in ticker_loads[:3]],
            }
        )

    if not factor_results:
        return {}

    # Determine if portfolio is concentrated on the dominant factor
    top_factor = factor_results[0]
    concentrated = top_factor["port_exposure"] > 0.60  # >60% exposure to one factor
    # Haircut: 0% at 60% exposure, 25% at 100% exposure
    haircut = 0.0
    if concentrated:
        haircut = min(25.0, (top_factor["port_exposure"] - 0.60) / 0.40 * 25.0)

    result = {
        "factors": factor_results,
        "concentration_warning": concentrated,
        "dominant_factor": top_factor["factor"],
        "dominant_exposure": top_factor["port_exposure"],
        "haircut_pct": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result
