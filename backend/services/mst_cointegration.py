"""
Dynamic Minimum Spanning Tree (MST) cointegration pairs discovery.

Replaces the 14 hard-coded pairs in cointegration.py with a universe-wide
graph that refreshes every Sunday.

Algorithm:
  1. Build pairwise correlation matrix from rolling 90-day returns.
  2. Convert to correlation-distance: D[i,j] = sqrt(2*(1 - |rho|)).
  3. Compute MST via Kruskal's algorithm (pure numpy — no scipy needed).
  4. Test each MST edge for Engle-Granger cointegration (ADF p < 0.05,
     rolling correlation >= 0.75).
  5. Persist passing pairs to data/mst_pairs_live.json (TTL 7 days).

Pairs are consumed by cointegration.get_pairs_signals() alongside the
static PAIRS list.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

log = logging.getLogger("signal.trade.mst_coint")

_DATA_DIR = Path(__file__).parent.parent / "data"
_CACHE_FILE = _DATA_DIR / "mst_pairs_live.json"
_CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

# Minimum requirements for a pair to be included
_MIN_CORR = 0.75  # rolling 90-day Pearson correlation
_MAX_COINT_P = 0.05  # Engle-Granger ADF p-value threshold
_MIN_WINDOW = 60  # minimum shared history required
_ROLL_WINDOW = 90  # correlation + spread estimation window


# ── Pure-numpy Kruskal MST ────────────────────────────────────────────────────


def _kruskal_mst(dist_matrix: np.ndarray) -> list[tuple[int, int, float]]:
    """
    Kruskal's algorithm on a symmetric distance matrix.
    Returns list of (i, j, weight) edges in the MST.
    """
    n = dist_matrix.shape[0]
    # Collect all unique edges above diagonal
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Union-Find
    parent = list(range(n))

    def _find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst_edges: list[tuple[int, int, float]] = []
    for weight, i, j in edges:
        ri, rj = _find(i), _find(j)
        if ri != rj:
            parent[ri] = rj
            mst_edges.append((i, j, float(weight)))
            if len(mst_edges) == n - 1:
                break

    return mst_edges


# ── Engle-Granger ADF cointegration test (scipy-based) ───────────────────────


def _engle_granger_p(va: np.ndarray, vb: np.ndarray) -> Optional[float]:
    """
    OLS residual ADF test.  Returns p-value, or None on failure.
    Uses scipy.stats.linregress + statsmodels adfuller when available,
    falls back to a manual ADF approximation otherwise.
    """
    try:
        from scipy import stats as _stats
        from statsmodels.tsa.stattools import adfuller

        slope, intercept, *_ = _stats.linregress(vb, va)
        residuals = va - (slope * vb + intercept)
        adf_result = adfuller(residuals, autolag="AIC", maxlag=5)
        return float(adf_result[1])  # p-value
    except Exception:
        return None


# ── Main public API ───────────────────────────────────────────────────────────


def compute_mst_pairs(
    price_matrix: pd.DataFrame,
    window: int = _ROLL_WINDOW,
) -> list[dict]:
    """
    Discover cointegrated pairs from a universe price matrix.

    Args:
        price_matrix: DataFrame, columns=tickers, index=date (recent history).
        window:       Rolling window in days for correlation and spread fitting.

    Returns:
        List of pair dicts compatible with cointegration.py candidate format:
          {t1, t2, beta, zscore, correlation, coint_p, distance}
    """
    tickers = [c for c in price_matrix.columns if not price_matrix[c].isnull().all()]
    if len(tickers) < 4:
        return []

    # Use only the last `window` trading days
    df = price_matrix[tickers].iloc[-window:].ffill().dropna(how="all", axis=1)
    tickers = list(df.columns)
    n = len(tickers)
    if n < 4:
        return []

    # Daily log-returns for correlation
    ret = np.log(df / df.shift(1)).dropna().values  # shape (T-1, n)
    T = ret.shape[0]
    if T < _MIN_WINDOW:
        return []

    # Pairwise Pearson correlation matrix
    corr = np.corrcoef(ret.T)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # Correlation distance: D[i,j] = sqrt(2 * (1 - |rho|))
    dist = np.sqrt(2.0 * (1.0 - np.abs(corr)))
    np.fill_diagonal(dist, 0.0)

    # MST
    mst_edges = _kruskal_mst(dist)
    log.debug("[mst] %d tickers → %d MST edges", n, len(mst_edges))

    prices = df.values  # shape (window, n)
    active_pairs: list[dict] = []

    for i, j, mst_dist in mst_edges:
        t1, t2 = tickers[i], tickers[j]

        va = prices[:, i].astype(float)
        vb = prices[:, j].astype(float)

        # Skip if insufficient overlap
        valid = ~(np.isnan(va) | np.isnan(vb))
        if valid.sum() < _MIN_WINDOW:
            continue

        va_v = va[valid]
        vb_v = vb[valid]

        # Rolling 90-day Pearson correlation
        roll_n = min(_ROLL_WINDOW, len(va_v))
        rolling_corr = float(np.corrcoef(va_v[-roll_n:], vb_v[-roll_n:])[0, 1])
        if abs(rolling_corr) < _MIN_CORR:
            continue

        # Engle-Granger cointegration p-value
        coint_p = _engle_granger_p(va_v, vb_v)
        if coint_p is None or coint_p > _MAX_COINT_P:
            continue

        # OLS beta and current z-score (train on first 80%, score last obs)
        cut = max(30, int(len(va_v) * 0.80))
        beta_num = np.cov(va_v[:cut], vb_v[:cut])[0, 1]
        beta_den = float(np.var(vb_v[:cut]))
        if abs(beta_den) < 1e-10:
            continue
        beta = beta_num / beta_den
        spread = va_v - beta * vb_v
        mu = float(spread[:cut].mean())
        sigma = float(spread[:cut].std())
        if sigma < 1e-8:
            continue
        zscore = (spread[-1] - mu) / sigma

        active_pairs.append(
            {
                "t1": t1,
                "t2": t2,
                "beta": round(float(beta), 6),
                "zscore": round(float(zscore), 3),
                "correlation": round(rolling_corr, 4),
                "coint_p": round(float(coint_p), 4),
                "distance": round(mst_dist, 4),
                "computed_at": time.time(),
            }
        )

    log.info("[mst] %d / %d MST edges pass cointegration filter", len(active_pairs), len(mst_edges))
    return active_pairs


async def refresh_mst_pairs(histories: dict[str, pd.DataFrame]) -> int:
    """
    Build price matrix from prefetched histories, compute MST pairs,
    and persist to data/mst_pairs_live.json.

    Returns number of pairs saved.  Called weekly from scanner.
    """
    import asyncio

    frames: dict[str, pd.Series] = {}
    for ticker, df in histories.items():
        if df is not None and "Close" in df.columns and len(df) >= _MIN_WINDOW:
            frames[ticker] = df["Close"].astype(float)

    if len(frames) < 5:
        log.warning("[mst] Too few histories (%d) to build MST", len(frames))
        return 0

    price_matrix = pd.DataFrame(frames).sort_index()

    pairs = await asyncio.to_thread(compute_mst_pairs, price_matrix)

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump({"pairs": pairs, "computed_at": time.time()}, f)

    log.info("[mst] Saved %d dynamic pairs to %s", len(pairs), _CACHE_FILE)
    return len(pairs)


def load_mst_pairs() -> list[dict]:
    """
    Load cached MST pairs from disk.  Returns [] if missing or stale (> 7 days).
    """
    if not _CACHE_FILE.exists():
        return []
    try:
        with open(_CACHE_FILE) as f:
            data = json.load(f)
        age = time.time() - float(data.get("computed_at", 0))
        if age > _CACHE_TTL_SECONDS:
            log.debug("[mst] Cache stale (%.0f days old)", age / 86400)
            return []
        return data.get("pairs", [])
    except Exception as e:
        log.debug("[mst] Cache load failed: %s", e)
        return []
