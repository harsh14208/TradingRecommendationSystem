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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__name_factor__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__name_factor__mutmut)
def _name_factor(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_orig(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_1(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = None
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_2(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w >= 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_3(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 1.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_4(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = None
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_5(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "XXUnidentifiedXX", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_6(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_7(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "UNIDENTIFIED", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_8(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 1
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_9(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = None
        if overlap > best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_10(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap >= best_overlap:
            best_overlap, best_factor = overlap, factor
    return best_factor


def x__name_factor__mutmut_11(tickers_loading: list[tuple[str, float]]) -> str:
    """Match the high-loading tickers to the closest named factor seed set."""
    high_loaders = {t for t, w in tickers_loading if w > 0.3}
    best_factor, best_overlap = "Unidentified", 0
    for factor, seeds in _FACTOR_SEEDS.items():
        overlap = len(high_loaders & set(seeds))
        if overlap > best_overlap:
            best_overlap, best_factor = None
    return best_factor

mutants_x__name_factor__mutmut['_mutmut_orig'] = x__name_factor__mutmut_orig # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_1'] = x__name_factor__mutmut_1 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_2'] = x__name_factor__mutmut_2 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_3'] = x__name_factor__mutmut_3 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_4'] = x__name_factor__mutmut_4 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_5'] = x__name_factor__mutmut_5 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_6'] = x__name_factor__mutmut_6 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_7'] = x__name_factor__mutmut_7 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_8'] = x__name_factor__mutmut_8 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_9'] = x__name_factor__mutmut_9 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_10'] = x__name_factor__mutmut_10 # type: ignore # mutmut generated
mutants_x__name_factor__mutmut['x__name_factor__mutmut_11'] = x__name_factor__mutmut_11 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_compute_pca_risk__mutmut)
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


async def x_compute_pca_risk__mutmut_orig(
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


async def x_compute_pca_risk__mutmut_1(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 61,
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


async def x_compute_pca_risk__mutmut_2(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = None
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


async def x_compute_pca_risk__mutmut_3(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = [t for t, v in positions.items() if v >= 0]
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


async def x_compute_pca_risk__mutmut_4(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = [t for t, v in positions.items() if v > 1]
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


async def x_compute_pca_risk__mutmut_5(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = [t for t, v in positions.items() if v > 0]
    if len(tickers) <= 3:
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


async def x_compute_pca_risk__mutmut_6(
    positions: dict[str, float],  # {ticker: market_value_usd}
    lookback_days: int = 60,
) -> dict:
    """
    Compute 2-factor PCA on position returns and return risk metrics.
    Falls back to empty dict if fewer than 3 positions or data unavailable.
    """
    tickers = [t for t, v in positions.items() if v > 0]
    if len(tickers) < 4:
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


async def x_compute_pca_risk__mutmut_7(
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

        histories = None
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


async def x_compute_pca_risk__mutmut_8(
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

        histories = await get_histories_batch(None, period="3mo", interval="1d")
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


async def x_compute_pca_risk__mutmut_9(
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

        histories = await get_histories_batch(tickers, period=None, interval="1d")
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


async def x_compute_pca_risk__mutmut_10(
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

        histories = await get_histories_batch(tickers, period="3mo", interval=None)
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


async def x_compute_pca_risk__mutmut_11(
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

        histories = await get_histories_batch(period="3mo", interval="1d")
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


async def x_compute_pca_risk__mutmut_12(
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

        histories = await get_histories_batch(tickers, interval="1d")
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


async def x_compute_pca_risk__mutmut_13(
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

        histories = await get_histories_batch(tickers, period="3mo", )
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


async def x_compute_pca_risk__mutmut_14(
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

        histories = await get_histories_batch(tickers, period="XX3moXX", interval="1d")
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


async def x_compute_pca_risk__mutmut_15(
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

        histories = await get_histories_batch(tickers, period="3MO", interval="1d")
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


async def x_compute_pca_risk__mutmut_16(
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

        histories = await get_histories_batch(tickers, period="3mo", interval="XX1dXX")
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


async def x_compute_pca_risk__mutmut_17(
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

        histories = await get_histories_batch(tickers, period="3mo", interval="1D")
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


async def x_compute_pca_risk__mutmut_18(
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
        log.debug(None)
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


async def x_compute_pca_risk__mutmut_19(
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
    returns_cols: dict[str, np.ndarray] = None
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


async def x_compute_pca_risk__mutmut_20(
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
    min_rows = None
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


async def x_compute_pca_risk__mutmut_21(
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
    min_rows = max(None, 20)
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


async def x_compute_pca_risk__mutmut_22(
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
    min_rows = max(lookback_days // 2, None)
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


async def x_compute_pca_risk__mutmut_23(
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
    min_rows = max(20)
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


async def x_compute_pca_risk__mutmut_24(
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
    min_rows = max(lookback_days // 2, )
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


async def x_compute_pca_risk__mutmut_25(
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
    min_rows = max(lookback_days / 2, 20)
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


async def x_compute_pca_risk__mutmut_26(
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
    min_rows = max(lookback_days // 3, 20)
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


async def x_compute_pca_risk__mutmut_27(
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
    min_rows = max(lookback_days // 2, 21)
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


async def x_compute_pca_risk__mutmut_28(
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
        df = None
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


async def x_compute_pca_risk__mutmut_29(
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
        df = histories.get(None)
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


async def x_compute_pca_risk__mutmut_30(
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
        if df is None and len(df) < min_rows:
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


async def x_compute_pca_risk__mutmut_31(
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
        if df is not None or len(df) < min_rows:
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


async def x_compute_pca_risk__mutmut_32(
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
        if df is None or len(df) <= min_rows:
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


async def x_compute_pca_risk__mutmut_33(
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
            break
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


async def x_compute_pca_risk__mutmut_34(
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
        closes = None
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


async def x_compute_pca_risk__mutmut_35(
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
        closes = df["Close"].astype(None).values[-lookback_days:]
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


async def x_compute_pca_risk__mutmut_36(
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
        closes = df["XXCloseXX"].astype(float).values[-lookback_days:]
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


async def x_compute_pca_risk__mutmut_37(
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
        closes = df["close"].astype(float).values[-lookback_days:]
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


async def x_compute_pca_risk__mutmut_38(
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
        closes = df["CLOSE"].astype(float).values[-lookback_days:]
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


async def x_compute_pca_risk__mutmut_39(
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
        closes = df["Close"].astype(float).values[+lookback_days:]
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


async def x_compute_pca_risk__mutmut_40(
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
        rets = None
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


async def x_compute_pca_risk__mutmut_41(
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
        rets = np.diff(closes) * closes[:-1]
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


async def x_compute_pca_risk__mutmut_42(
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
        rets = np.diff(None) / closes[:-1]
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


async def x_compute_pca_risk__mutmut_43(
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
        rets = np.diff(closes) / closes[:+1]
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


async def x_compute_pca_risk__mutmut_44(
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
        rets = np.diff(closes) / closes[:-2]
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


async def x_compute_pca_risk__mutmut_45(
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
        returns_cols[t] = None

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


async def x_compute_pca_risk__mutmut_46(
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

    if len(returns_cols) <= 3:
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


async def x_compute_pca_risk__mutmut_47(
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

    if len(returns_cols) < 4:
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


async def x_compute_pca_risk__mutmut_48(
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
    min_len = None
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


async def x_compute_pca_risk__mutmut_49(
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
    min_len = min(None)
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


async def x_compute_pca_risk__mutmut_50(
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
    R = None
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


async def x_compute_pca_risk__mutmut_51(
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
    R = np.column_stack(None)
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


async def x_compute_pca_risk__mutmut_52(
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
    R = np.column_stack([v[+min_len:] for v in returns_cols.values()])
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


async def x_compute_pca_risk__mutmut_53(
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
    col_tickers = None

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


async def x_compute_pca_risk__mutmut_54(
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
    col_tickers = list(None)

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


async def x_compute_pca_risk__mutmut_55(
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
    R = R.mean(axis=0)
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


async def x_compute_pca_risk__mutmut_56(
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
    R += R.mean(axis=0)
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


async def x_compute_pca_risk__mutmut_57(
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
    R -= R.mean(axis=None)
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


async def x_compute_pca_risk__mutmut_58(
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
    R -= R.mean(axis=1)
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


async def x_compute_pca_risk__mutmut_59(
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
    stds = None
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


async def x_compute_pca_risk__mutmut_60(
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
    stds = R.std(axis=None)
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


async def x_compute_pca_risk__mutmut_61(
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
    stds = R.std(axis=1)
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


async def x_compute_pca_risk__mutmut_62(
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
    stds[stds == 0] = None
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


async def x_compute_pca_risk__mutmut_63(
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
    stds[stds != 0] = 1.0
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


async def x_compute_pca_risk__mutmut_64(
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
    stds[stds == 1] = 1.0
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


async def x_compute_pca_risk__mutmut_65(
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
    stds[stds == 0] = 2.0
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


async def x_compute_pca_risk__mutmut_66(
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
    R = stds

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


async def x_compute_pca_risk__mutmut_67(
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
    R *= stds

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


async def x_compute_pca_risk__mutmut_68(
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
    corr = None
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


async def x_compute_pca_risk__mutmut_69(
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
    corr = np.corrcoef(None)
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


async def x_compute_pca_risk__mutmut_70(
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
    eigvals, eigvecs = None
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


async def x_compute_pca_risk__mutmut_71(
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
    eigvals, eigvecs = np.linalg.eigh(None)
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


async def x_compute_pca_risk__mutmut_72(
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
    idx = None
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


async def x_compute_pca_risk__mutmut_73(
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
    idx = np.argsort(None)[::-1]
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


async def x_compute_pca_risk__mutmut_74(
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
    idx = np.argsort(eigvals)[::+1]
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


async def x_compute_pca_risk__mutmut_75(
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
    idx = np.argsort(eigvals)[::-2]
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


async def x_compute_pca_risk__mutmut_76(
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
    eigvals = None
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


async def x_compute_pca_risk__mutmut_77(
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
    eigvecs = None

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


async def x_compute_pca_risk__mutmut_78(
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

    total_var = None
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


async def x_compute_pca_risk__mutmut_79(
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
    factor_results = None

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


async def x_compute_pca_risk__mutmut_80(
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

    for fi in range(None):
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


async def x_compute_pca_risk__mutmut_81(
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

    for fi in range(min(None, len(eigvals))):
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


async def x_compute_pca_risk__mutmut_82(
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

    for fi in range(min(2, None)):
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


async def x_compute_pca_risk__mutmut_83(
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

    for fi in range(min(len(eigvals))):
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


async def x_compute_pca_risk__mutmut_84(
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

    for fi in range(min(2, )):
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


async def x_compute_pca_risk__mutmut_85(
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

    for fi in range(min(3, len(eigvals))):
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


async def x_compute_pca_risk__mutmut_86(
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
        loadings = None
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


async def x_compute_pca_risk__mutmut_87(
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
        variance_pct = None
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


async def x_compute_pca_risk__mutmut_88(
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
        variance_pct = round(None, 1)
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


async def x_compute_pca_risk__mutmut_89(
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
        variance_pct = round(eigvals[fi] / total_var * 100, None)
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


async def x_compute_pca_risk__mutmut_90(
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
        variance_pct = round(1)
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


async def x_compute_pca_risk__mutmut_91(
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
        variance_pct = round(eigvals[fi] / total_var * 100, )
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


async def x_compute_pca_risk__mutmut_92(
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
        variance_pct = round(eigvals[fi] / total_var / 100, 1)
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


async def x_compute_pca_risk__mutmut_93(
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
        variance_pct = round(eigvals[fi] * total_var * 100, 1)
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


async def x_compute_pca_risk__mutmut_94(
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
        variance_pct = round(eigvals[fi] / total_var * 101, 1)
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


async def x_compute_pca_risk__mutmut_95(
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
        variance_pct = round(eigvals[fi] / total_var * 100, 2)
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


async def x_compute_pca_risk__mutmut_96(
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
        ticker_loads = None
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


async def x_compute_pca_risk__mutmut_97(
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
        ticker_loads = sorted(None, key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_98(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=None)
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


async def x_compute_pca_risk__mutmut_99(
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
        ticker_loads = sorted(key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_100(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), )
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


async def x_compute_pca_risk__mutmut_101(
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
        ticker_loads = sorted(zip(None, loadings.tolist()), key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_102(
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
        ticker_loads = sorted(zip(col_tickers, None), key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_103(
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
        ticker_loads = sorted(zip(loadings.tolist()), key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_104(
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
        ticker_loads = sorted(zip(col_tickers, ), key=lambda x: -abs(x[1]))
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


async def x_compute_pca_risk__mutmut_105(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=lambda x: None)
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


async def x_compute_pca_risk__mutmut_106(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=lambda x: +abs(x[1]))
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


async def x_compute_pca_risk__mutmut_107(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=lambda x: -abs(None))
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


async def x_compute_pca_risk__mutmut_108(
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
        ticker_loads = sorted(zip(col_tickers, loadings.tolist()), key=lambda x: -abs(x[2]))
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


async def x_compute_pca_risk__mutmut_109(
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
        factor_name = None
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


async def x_compute_pca_risk__mutmut_110(
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
        factor_name = _name_factor(None)
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


async def x_compute_pca_risk__mutmut_111(
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
        max_load = None

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


async def x_compute_pca_risk__mutmut_112(
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
        max_load = float(None)

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


async def x_compute_pca_risk__mutmut_113(
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
        max_load = float(abs(None).max())

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


async def x_compute_pca_risk__mutmut_114(
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
        total_mv = None
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


async def x_compute_pca_risk__mutmut_115(
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
        total_mv = sum(None)
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


async def x_compute_pca_risk__mutmut_116(
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
        total_mv = sum(positions.get(None, 0) for t in col_tickers)
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


async def x_compute_pca_risk__mutmut_117(
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
        total_mv = sum(positions.get(t, None) for t in col_tickers)
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


async def x_compute_pca_risk__mutmut_118(
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
        total_mv = sum(positions.get(0) for t in col_tickers)
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


async def x_compute_pca_risk__mutmut_119(
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
        total_mv = sum(positions.get(t, ) for t in col_tickers)
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


async def x_compute_pca_risk__mutmut_120(
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
        total_mv = sum(positions.get(t, 1) for t in col_tickers)
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


async def x_compute_pca_risk__mutmut_121(
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
        port_exposure = None
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


async def x_compute_pca_risk__mutmut_122(
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
        port_exposure = 1.0
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


async def x_compute_pca_risk__mutmut_123(
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
        if total_mv >= 0:
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


async def x_compute_pca_risk__mutmut_124(
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
        if total_mv > 1:
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


async def x_compute_pca_risk__mutmut_125(
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
            for t, load in zip(None, loadings):
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


async def x_compute_pca_risk__mutmut_126(
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
            for t, load in zip(col_tickers, None):
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


async def x_compute_pca_risk__mutmut_127(
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
            for t, load in zip(loadings):
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


async def x_compute_pca_risk__mutmut_128(
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
            for t, load in zip(col_tickers, ):
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


async def x_compute_pca_risk__mutmut_129(
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
                port_exposure = (positions.get(t, 0) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_130(
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
                port_exposure -= (positions.get(t, 0) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_131(
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
                port_exposure += (positions.get(t, 0) / total_mv) / abs(load)

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


async def x_compute_pca_risk__mutmut_132(
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
                port_exposure += (positions.get(t, 0) * total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_133(
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
                port_exposure += (positions.get(None, 0) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_134(
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
                port_exposure += (positions.get(t, None) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_135(
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
                port_exposure += (positions.get(0) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_136(
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
                port_exposure += (positions.get(t, ) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_137(
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
                port_exposure += (positions.get(t, 1) / total_mv) * abs(load)

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


async def x_compute_pca_risk__mutmut_138(
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
                port_exposure += (positions.get(t, 0) / total_mv) * abs(None)

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


async def x_compute_pca_risk__mutmut_139(
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
            None
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


async def x_compute_pca_risk__mutmut_140(
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
                "XXfactorXX": factor_name,
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


async def x_compute_pca_risk__mutmut_141(
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
                "FACTOR": factor_name,
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


async def x_compute_pca_risk__mutmut_142(
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
                "XXfactor_numXX": fi + 1,
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


async def x_compute_pca_risk__mutmut_143(
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
                "FACTOR_NUM": fi + 1,
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


async def x_compute_pca_risk__mutmut_144(
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
                "factor_num": fi - 1,
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


async def x_compute_pca_risk__mutmut_145(
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
                "factor_num": fi + 2,
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


async def x_compute_pca_risk__mutmut_146(
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
                "XXvariance_pctXX": variance_pct,
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


async def x_compute_pca_risk__mutmut_147(
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
                "VARIANCE_PCT": variance_pct,
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


async def x_compute_pca_risk__mutmut_148(
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
                "XXmax_loadingXX": round(max_load, 3),
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


async def x_compute_pca_risk__mutmut_149(
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
                "MAX_LOADING": round(max_load, 3),
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


async def x_compute_pca_risk__mutmut_150(
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
                "max_loading": round(None, 3),
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


async def x_compute_pca_risk__mutmut_151(
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
                "max_loading": round(max_load, None),
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


async def x_compute_pca_risk__mutmut_152(
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
                "max_loading": round(3),
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


async def x_compute_pca_risk__mutmut_153(
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
                "max_loading": round(max_load, ),
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


async def x_compute_pca_risk__mutmut_154(
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
                "max_loading": round(max_load, 4),
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


async def x_compute_pca_risk__mutmut_155(
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
                "XXport_exposureXX": round(port_exposure, 3),
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


async def x_compute_pca_risk__mutmut_156(
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
                "PORT_EXPOSURE": round(port_exposure, 3),
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


async def x_compute_pca_risk__mutmut_157(
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
                "port_exposure": round(None, 3),
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


async def x_compute_pca_risk__mutmut_158(
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
                "port_exposure": round(port_exposure, None),
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


async def x_compute_pca_risk__mutmut_159(
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
                "port_exposure": round(3),
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


async def x_compute_pca_risk__mutmut_160(
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
                "port_exposure": round(port_exposure, ),
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


async def x_compute_pca_risk__mutmut_161(
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
                "port_exposure": round(port_exposure, 4),
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


async def x_compute_pca_risk__mutmut_162(
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
                "XXtop_tickersXX": [t for t, _ in ticker_loads[:3]],
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


async def x_compute_pca_risk__mutmut_163(
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
                "TOP_TICKERS": [t for t, _ in ticker_loads[:3]],
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


async def x_compute_pca_risk__mutmut_164(
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
                "top_tickers": [t for t, _ in ticker_loads[:4]],
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


async def x_compute_pca_risk__mutmut_165(
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

    if factor_results:
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


async def x_compute_pca_risk__mutmut_166(
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
    top_factor = None
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


async def x_compute_pca_risk__mutmut_167(
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
    top_factor = factor_results[1]
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


async def x_compute_pca_risk__mutmut_168(
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
    concentrated = None  # >60% exposure to one factor
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


async def x_compute_pca_risk__mutmut_169(
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
    concentrated = top_factor["XXport_exposureXX"] > 0.60  # >60% exposure to one factor
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


async def x_compute_pca_risk__mutmut_170(
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
    concentrated = top_factor["PORT_EXPOSURE"] > 0.60  # >60% exposure to one factor
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


async def x_compute_pca_risk__mutmut_171(
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
    concentrated = top_factor["port_exposure"] >= 0.60  # >60% exposure to one factor
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


async def x_compute_pca_risk__mutmut_172(
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
    concentrated = top_factor["port_exposure"] > 1.6  # >60% exposure to one factor
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


async def x_compute_pca_risk__mutmut_173(
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
    haircut = None
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


async def x_compute_pca_risk__mutmut_174(
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
    haircut = 1.0
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


async def x_compute_pca_risk__mutmut_175(
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
        haircut = None

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


async def x_compute_pca_risk__mutmut_176(
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
        haircut = min(None, (top_factor["port_exposure"] - 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_177(
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
        haircut = min(25.0, None)

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


async def x_compute_pca_risk__mutmut_178(
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
        haircut = min((top_factor["port_exposure"] - 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_179(
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
        haircut = min(25.0, )

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


async def x_compute_pca_risk__mutmut_180(
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
        haircut = min(26.0, (top_factor["port_exposure"] - 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_181(
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
        haircut = min(25.0, (top_factor["port_exposure"] - 0.60) / 0.40 / 25.0)

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


async def x_compute_pca_risk__mutmut_182(
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
        haircut = min(25.0, (top_factor["port_exposure"] - 0.60) * 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_183(
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
        haircut = min(25.0, (top_factor["port_exposure"] + 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_184(
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
        haircut = min(25.0, (top_factor["XXport_exposureXX"] - 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_185(
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
        haircut = min(25.0, (top_factor["PORT_EXPOSURE"] - 0.60) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_186(
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
        haircut = min(25.0, (top_factor["port_exposure"] - 1.6) / 0.40 * 25.0)

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


async def x_compute_pca_risk__mutmut_187(
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
        haircut = min(25.0, (top_factor["port_exposure"] - 0.60) / 1.4 * 25.0)

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


async def x_compute_pca_risk__mutmut_188(
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
        haircut = min(25.0, (top_factor["port_exposure"] - 0.60) / 0.40 * 26.0)

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


async def x_compute_pca_risk__mutmut_189(
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

    result = None
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_190(
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
        "XXfactorsXX": factor_results,
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


async def x_compute_pca_risk__mutmut_191(
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
        "FACTORS": factor_results,
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


async def x_compute_pca_risk__mutmut_192(
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
        "XXconcentration_warningXX": concentrated,
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


async def x_compute_pca_risk__mutmut_193(
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
        "CONCENTRATION_WARNING": concentrated,
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


async def x_compute_pca_risk__mutmut_194(
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
        "XXdominant_factorXX": top_factor["factor"],
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


async def x_compute_pca_risk__mutmut_195(
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
        "DOMINANT_FACTOR": top_factor["factor"],
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


async def x_compute_pca_risk__mutmut_196(
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
        "dominant_factor": top_factor["XXfactorXX"],
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


async def x_compute_pca_risk__mutmut_197(
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
        "dominant_factor": top_factor["FACTOR"],
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


async def x_compute_pca_risk__mutmut_198(
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
        "XXdominant_exposureXX": top_factor["port_exposure"],
        "haircut_pct": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_199(
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
        "DOMINANT_EXPOSURE": top_factor["port_exposure"],
        "haircut_pct": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_200(
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
        "dominant_exposure": top_factor["XXport_exposureXX"],
        "haircut_pct": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_201(
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
        "dominant_exposure": top_factor["PORT_EXPOSURE"],
        "haircut_pct": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_202(
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
        "XXhaircut_pctXX": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_203(
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
        "HAIRCUT_PCT": round(haircut, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_204(
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
        "haircut_pct": round(None, 1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_205(
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
        "haircut_pct": round(haircut, None),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_206(
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
        "haircut_pct": round(1),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_207(
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
        "haircut_pct": round(haircut, ),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_208(
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
        "haircut_pct": round(haircut, 2),
        "tickers_analysed": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_209(
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
        "XXtickers_analysedXX": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_210(
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
        "TICKERS_ANALYSED": col_tickers,
    }
    if concentrated:
        log.info(
            f"[pca_risk] Portfolio concentrated on '{top_factor['factor']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_211(
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
            None
        )
    return result


async def x_compute_pca_risk__mutmut_212(
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
            f"[pca_risk] Portfolio concentrated on '{top_factor['XXfactorXX']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_213(
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
            f"[pca_risk] Portfolio concentrated on '{top_factor['FACTOR']}' "
            f"({top_factor['port_exposure']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_214(
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
            f"({top_factor['XXport_exposureXX']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result


async def x_compute_pca_risk__mutmut_215(
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
            f"({top_factor['PORT_EXPOSURE']:.0%} exposure) — haircut={haircut:.0f}%"
        )
    return result

mutants_x_compute_pca_risk__mutmut['_mutmut_orig'] = x_compute_pca_risk__mutmut_orig # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_1'] = x_compute_pca_risk__mutmut_1 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_2'] = x_compute_pca_risk__mutmut_2 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_3'] = x_compute_pca_risk__mutmut_3 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_4'] = x_compute_pca_risk__mutmut_4 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_5'] = x_compute_pca_risk__mutmut_5 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_6'] = x_compute_pca_risk__mutmut_6 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_7'] = x_compute_pca_risk__mutmut_7 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_8'] = x_compute_pca_risk__mutmut_8 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_9'] = x_compute_pca_risk__mutmut_9 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_10'] = x_compute_pca_risk__mutmut_10 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_11'] = x_compute_pca_risk__mutmut_11 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_12'] = x_compute_pca_risk__mutmut_12 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_13'] = x_compute_pca_risk__mutmut_13 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_14'] = x_compute_pca_risk__mutmut_14 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_15'] = x_compute_pca_risk__mutmut_15 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_16'] = x_compute_pca_risk__mutmut_16 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_17'] = x_compute_pca_risk__mutmut_17 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_18'] = x_compute_pca_risk__mutmut_18 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_19'] = x_compute_pca_risk__mutmut_19 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_20'] = x_compute_pca_risk__mutmut_20 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_21'] = x_compute_pca_risk__mutmut_21 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_22'] = x_compute_pca_risk__mutmut_22 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_23'] = x_compute_pca_risk__mutmut_23 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_24'] = x_compute_pca_risk__mutmut_24 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_25'] = x_compute_pca_risk__mutmut_25 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_26'] = x_compute_pca_risk__mutmut_26 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_27'] = x_compute_pca_risk__mutmut_27 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_28'] = x_compute_pca_risk__mutmut_28 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_29'] = x_compute_pca_risk__mutmut_29 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_30'] = x_compute_pca_risk__mutmut_30 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_31'] = x_compute_pca_risk__mutmut_31 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_32'] = x_compute_pca_risk__mutmut_32 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_33'] = x_compute_pca_risk__mutmut_33 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_34'] = x_compute_pca_risk__mutmut_34 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_35'] = x_compute_pca_risk__mutmut_35 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_36'] = x_compute_pca_risk__mutmut_36 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_37'] = x_compute_pca_risk__mutmut_37 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_38'] = x_compute_pca_risk__mutmut_38 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_39'] = x_compute_pca_risk__mutmut_39 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_40'] = x_compute_pca_risk__mutmut_40 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_41'] = x_compute_pca_risk__mutmut_41 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_42'] = x_compute_pca_risk__mutmut_42 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_43'] = x_compute_pca_risk__mutmut_43 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_44'] = x_compute_pca_risk__mutmut_44 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_45'] = x_compute_pca_risk__mutmut_45 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_46'] = x_compute_pca_risk__mutmut_46 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_47'] = x_compute_pca_risk__mutmut_47 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_48'] = x_compute_pca_risk__mutmut_48 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_49'] = x_compute_pca_risk__mutmut_49 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_50'] = x_compute_pca_risk__mutmut_50 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_51'] = x_compute_pca_risk__mutmut_51 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_52'] = x_compute_pca_risk__mutmut_52 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_53'] = x_compute_pca_risk__mutmut_53 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_54'] = x_compute_pca_risk__mutmut_54 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_55'] = x_compute_pca_risk__mutmut_55 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_56'] = x_compute_pca_risk__mutmut_56 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_57'] = x_compute_pca_risk__mutmut_57 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_58'] = x_compute_pca_risk__mutmut_58 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_59'] = x_compute_pca_risk__mutmut_59 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_60'] = x_compute_pca_risk__mutmut_60 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_61'] = x_compute_pca_risk__mutmut_61 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_62'] = x_compute_pca_risk__mutmut_62 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_63'] = x_compute_pca_risk__mutmut_63 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_64'] = x_compute_pca_risk__mutmut_64 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_65'] = x_compute_pca_risk__mutmut_65 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_66'] = x_compute_pca_risk__mutmut_66 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_67'] = x_compute_pca_risk__mutmut_67 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_68'] = x_compute_pca_risk__mutmut_68 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_69'] = x_compute_pca_risk__mutmut_69 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_70'] = x_compute_pca_risk__mutmut_70 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_71'] = x_compute_pca_risk__mutmut_71 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_72'] = x_compute_pca_risk__mutmut_72 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_73'] = x_compute_pca_risk__mutmut_73 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_74'] = x_compute_pca_risk__mutmut_74 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_75'] = x_compute_pca_risk__mutmut_75 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_76'] = x_compute_pca_risk__mutmut_76 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_77'] = x_compute_pca_risk__mutmut_77 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_78'] = x_compute_pca_risk__mutmut_78 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_79'] = x_compute_pca_risk__mutmut_79 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_80'] = x_compute_pca_risk__mutmut_80 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_81'] = x_compute_pca_risk__mutmut_81 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_82'] = x_compute_pca_risk__mutmut_82 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_83'] = x_compute_pca_risk__mutmut_83 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_84'] = x_compute_pca_risk__mutmut_84 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_85'] = x_compute_pca_risk__mutmut_85 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_86'] = x_compute_pca_risk__mutmut_86 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_87'] = x_compute_pca_risk__mutmut_87 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_88'] = x_compute_pca_risk__mutmut_88 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_89'] = x_compute_pca_risk__mutmut_89 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_90'] = x_compute_pca_risk__mutmut_90 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_91'] = x_compute_pca_risk__mutmut_91 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_92'] = x_compute_pca_risk__mutmut_92 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_93'] = x_compute_pca_risk__mutmut_93 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_94'] = x_compute_pca_risk__mutmut_94 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_95'] = x_compute_pca_risk__mutmut_95 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_96'] = x_compute_pca_risk__mutmut_96 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_97'] = x_compute_pca_risk__mutmut_97 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_98'] = x_compute_pca_risk__mutmut_98 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_99'] = x_compute_pca_risk__mutmut_99 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_100'] = x_compute_pca_risk__mutmut_100 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_101'] = x_compute_pca_risk__mutmut_101 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_102'] = x_compute_pca_risk__mutmut_102 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_103'] = x_compute_pca_risk__mutmut_103 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_104'] = x_compute_pca_risk__mutmut_104 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_105'] = x_compute_pca_risk__mutmut_105 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_106'] = x_compute_pca_risk__mutmut_106 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_107'] = x_compute_pca_risk__mutmut_107 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_108'] = x_compute_pca_risk__mutmut_108 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_109'] = x_compute_pca_risk__mutmut_109 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_110'] = x_compute_pca_risk__mutmut_110 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_111'] = x_compute_pca_risk__mutmut_111 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_112'] = x_compute_pca_risk__mutmut_112 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_113'] = x_compute_pca_risk__mutmut_113 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_114'] = x_compute_pca_risk__mutmut_114 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_115'] = x_compute_pca_risk__mutmut_115 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_116'] = x_compute_pca_risk__mutmut_116 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_117'] = x_compute_pca_risk__mutmut_117 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_118'] = x_compute_pca_risk__mutmut_118 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_119'] = x_compute_pca_risk__mutmut_119 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_120'] = x_compute_pca_risk__mutmut_120 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_121'] = x_compute_pca_risk__mutmut_121 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_122'] = x_compute_pca_risk__mutmut_122 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_123'] = x_compute_pca_risk__mutmut_123 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_124'] = x_compute_pca_risk__mutmut_124 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_125'] = x_compute_pca_risk__mutmut_125 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_126'] = x_compute_pca_risk__mutmut_126 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_127'] = x_compute_pca_risk__mutmut_127 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_128'] = x_compute_pca_risk__mutmut_128 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_129'] = x_compute_pca_risk__mutmut_129 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_130'] = x_compute_pca_risk__mutmut_130 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_131'] = x_compute_pca_risk__mutmut_131 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_132'] = x_compute_pca_risk__mutmut_132 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_133'] = x_compute_pca_risk__mutmut_133 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_134'] = x_compute_pca_risk__mutmut_134 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_135'] = x_compute_pca_risk__mutmut_135 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_136'] = x_compute_pca_risk__mutmut_136 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_137'] = x_compute_pca_risk__mutmut_137 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_138'] = x_compute_pca_risk__mutmut_138 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_139'] = x_compute_pca_risk__mutmut_139 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_140'] = x_compute_pca_risk__mutmut_140 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_141'] = x_compute_pca_risk__mutmut_141 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_142'] = x_compute_pca_risk__mutmut_142 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_143'] = x_compute_pca_risk__mutmut_143 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_144'] = x_compute_pca_risk__mutmut_144 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_145'] = x_compute_pca_risk__mutmut_145 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_146'] = x_compute_pca_risk__mutmut_146 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_147'] = x_compute_pca_risk__mutmut_147 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_148'] = x_compute_pca_risk__mutmut_148 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_149'] = x_compute_pca_risk__mutmut_149 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_150'] = x_compute_pca_risk__mutmut_150 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_151'] = x_compute_pca_risk__mutmut_151 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_152'] = x_compute_pca_risk__mutmut_152 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_153'] = x_compute_pca_risk__mutmut_153 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_154'] = x_compute_pca_risk__mutmut_154 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_155'] = x_compute_pca_risk__mutmut_155 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_156'] = x_compute_pca_risk__mutmut_156 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_157'] = x_compute_pca_risk__mutmut_157 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_158'] = x_compute_pca_risk__mutmut_158 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_159'] = x_compute_pca_risk__mutmut_159 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_160'] = x_compute_pca_risk__mutmut_160 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_161'] = x_compute_pca_risk__mutmut_161 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_162'] = x_compute_pca_risk__mutmut_162 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_163'] = x_compute_pca_risk__mutmut_163 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_164'] = x_compute_pca_risk__mutmut_164 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_165'] = x_compute_pca_risk__mutmut_165 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_166'] = x_compute_pca_risk__mutmut_166 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_167'] = x_compute_pca_risk__mutmut_167 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_168'] = x_compute_pca_risk__mutmut_168 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_169'] = x_compute_pca_risk__mutmut_169 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_170'] = x_compute_pca_risk__mutmut_170 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_171'] = x_compute_pca_risk__mutmut_171 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_172'] = x_compute_pca_risk__mutmut_172 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_173'] = x_compute_pca_risk__mutmut_173 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_174'] = x_compute_pca_risk__mutmut_174 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_175'] = x_compute_pca_risk__mutmut_175 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_176'] = x_compute_pca_risk__mutmut_176 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_177'] = x_compute_pca_risk__mutmut_177 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_178'] = x_compute_pca_risk__mutmut_178 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_179'] = x_compute_pca_risk__mutmut_179 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_180'] = x_compute_pca_risk__mutmut_180 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_181'] = x_compute_pca_risk__mutmut_181 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_182'] = x_compute_pca_risk__mutmut_182 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_183'] = x_compute_pca_risk__mutmut_183 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_184'] = x_compute_pca_risk__mutmut_184 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_185'] = x_compute_pca_risk__mutmut_185 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_186'] = x_compute_pca_risk__mutmut_186 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_187'] = x_compute_pca_risk__mutmut_187 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_188'] = x_compute_pca_risk__mutmut_188 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_189'] = x_compute_pca_risk__mutmut_189 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_190'] = x_compute_pca_risk__mutmut_190 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_191'] = x_compute_pca_risk__mutmut_191 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_192'] = x_compute_pca_risk__mutmut_192 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_193'] = x_compute_pca_risk__mutmut_193 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_194'] = x_compute_pca_risk__mutmut_194 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_195'] = x_compute_pca_risk__mutmut_195 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_196'] = x_compute_pca_risk__mutmut_196 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_197'] = x_compute_pca_risk__mutmut_197 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_198'] = x_compute_pca_risk__mutmut_198 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_199'] = x_compute_pca_risk__mutmut_199 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_200'] = x_compute_pca_risk__mutmut_200 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_201'] = x_compute_pca_risk__mutmut_201 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_202'] = x_compute_pca_risk__mutmut_202 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_203'] = x_compute_pca_risk__mutmut_203 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_204'] = x_compute_pca_risk__mutmut_204 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_205'] = x_compute_pca_risk__mutmut_205 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_206'] = x_compute_pca_risk__mutmut_206 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_207'] = x_compute_pca_risk__mutmut_207 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_208'] = x_compute_pca_risk__mutmut_208 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_209'] = x_compute_pca_risk__mutmut_209 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_210'] = x_compute_pca_risk__mutmut_210 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_211'] = x_compute_pca_risk__mutmut_211 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_212'] = x_compute_pca_risk__mutmut_212 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_213'] = x_compute_pca_risk__mutmut_213 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_214'] = x_compute_pca_risk__mutmut_214 # type: ignore # mutmut generated
mutants_x_compute_pca_risk__mutmut['x_compute_pca_risk__mutmut_215'] = x_compute_pca_risk__mutmut_215 # type: ignore # mutmut generated
