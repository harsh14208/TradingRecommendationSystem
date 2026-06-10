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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_returns__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_returns__mutmut)
async def _fetch_returns(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
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


async def x__fetch_returns__mutmut_orig(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
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


async def x__fetch_returns__mutmut_1(tickers: list[str], period: str = "XX3moXX") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
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


async def x__fetch_returns__mutmut_2(tickers: list[str], period: str = "3MO") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
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


async def x__fetch_returns__mutmut_3(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = None
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


async def x__fetch_returns__mutmut_4(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(None, period=period, interval="1d")
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


async def x__fetch_returns__mutmut_5(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=None, interval="1d")
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


async def x__fetch_returns__mutmut_6(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval=None)
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


async def x__fetch_returns__mutmut_7(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(period=period, interval="1d")
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


async def x__fetch_returns__mutmut_8(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, interval="1d")
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


async def x__fetch_returns__mutmut_9(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, )
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


async def x__fetch_returns__mutmut_10(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="XX1dXX")
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


async def x__fetch_returns__mutmut_11(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1D")
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


async def x__fetch_returns__mutmut_12(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = None
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_13(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = None
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_14(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(None)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_15(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty and len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_16(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None and df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_17(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is not None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_18(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) <= 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_19(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 11:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_20(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            break
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_21(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = None
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_22(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(None)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_23(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["XXCloseXX"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_24(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_25(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["CLOSE"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_26(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = None
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_27(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if returns:
        return pd.DataFrame()
    return pd.DataFrame(returns).dropna()


async def x__fetch_returns__mutmut_28(tickers: list[str], period: str = "3mo") -> pd.DataFrame:
    """Fetch daily % returns for each ticker. Returns DataFrame[ticker → daily_return]."""
    from services.market_data import get_histories_batch

    histories = await get_histories_batch(tickers, period=period, interval="1d")
    returns: dict[str, pd.Series] = {}
    for t in tickers:
        df = histories.get(t)
        if df is None or df.empty or len(df) < 10:
            continue
        closes = df["Close"].astype(float)
        returns[t] = closes.pct_change().dropna()
    if not returns:
        return pd.DataFrame()
    return pd.DataFrame(None).dropna()

mutants_x__fetch_returns__mutmut['_mutmut_orig'] = x__fetch_returns__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_1'] = x__fetch_returns__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_2'] = x__fetch_returns__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_3'] = x__fetch_returns__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_4'] = x__fetch_returns__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_5'] = x__fetch_returns__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_6'] = x__fetch_returns__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_7'] = x__fetch_returns__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_8'] = x__fetch_returns__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_9'] = x__fetch_returns__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_10'] = x__fetch_returns__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_11'] = x__fetch_returns__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_12'] = x__fetch_returns__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_13'] = x__fetch_returns__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_14'] = x__fetch_returns__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_15'] = x__fetch_returns__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_16'] = x__fetch_returns__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_17'] = x__fetch_returns__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_18'] = x__fetch_returns__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_19'] = x__fetch_returns__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_20'] = x__fetch_returns__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_21'] = x__fetch_returns__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_22'] = x__fetch_returns__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_23'] = x__fetch_returns__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_24'] = x__fetch_returns__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_25'] = x__fetch_returns__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_26'] = x__fetch_returns__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_27'] = x__fetch_returns__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_returns__mutmut['x__fetch_returns__mutmut_28'] = x__fetch_returns__mutmut_28 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__vol_target_weights__mutmut)
def _vol_target_weights(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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


def x__vol_target_weights__mutmut_orig(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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


def x__vol_target_weights__mutmut_1(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty and len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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


def x__vol_target_weights__mutmut_2(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) <= 1:
        return {}

    tickers = list(returns_df.columns)

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


def x__vol_target_weights__mutmut_3(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 2:
        return {}

    tickers = list(returns_df.columns)

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


def x__vol_target_weights__mutmut_4(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = None

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


def x__vol_target_weights__mutmut_5(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(None)

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


def x__vol_target_weights__mutmut_6(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = None

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


def x__vol_target_weights__mutmut_7(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(None) for t in tickers}

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


def x__vol_target_weights__mutmut_8(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() / np.sqrt(TRADING_DAYS)) for t in tickers}

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


def x__vol_target_weights__mutmut_9(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(None)) for t in tickers}

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


def x__vol_target_weights__mutmut_10(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = None
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


def x__vol_target_weights__mutmut_11(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 * vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
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


def x__vol_target_weights__mutmut_12(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 2.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
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


def x__vol_target_weights__mutmut_13(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] >= 1e-6 else 0.0 for t in tickers}
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


def x__vol_target_weights__mutmut_14(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1.000001 else 0.0 for t in tickers}
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


def x__vol_target_weights__mutmut_15(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 1.0 for t in tickers}
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


def x__vol_target_weights__mutmut_16(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = None
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


def x__vol_target_weights__mutmut_17(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) and 1.0
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


def x__vol_target_weights__mutmut_18(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(None) or 1.0
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


def x__vol_target_weights__mutmut_19(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 2.0
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


def x__vol_target_weights__mutmut_20(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 1.0
    raw_weights = None

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


def x__vol_target_weights__mutmut_21(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 1.0
    raw_weights = {t: inv_vols[t] * total_inv for t in tickers}

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


def x__vol_target_weights__mutmut_22(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 1.0
    raw_weights = {t: inv_vols[t] / total_inv for t in tickers}

    # Correlation matrix
    corr_matrix = None

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


def x__vol_target_weights__mutmut_23(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

    # Annualised volatility per asset
    vols = {t: float(returns_df[t].std() * np.sqrt(TRADING_DAYS)) for t in tickers}

    # Inverse-vol weights (baseline)
    inv_vols = {t: 1.0 / vols[t] if vols[t] > 1e-6 else 0.0 for t in tickers}
    total_inv = sum(inv_vols.values()) or 1.0
    raw_weights = {t: inv_vols[t] / total_inv for t in tickers}

    # Correlation matrix
    corr_matrix = returns_df.corr()

    # Collect high-correlation pairs and apply penalty
    high_corr_pairs = None
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


def x__vol_target_weights__mutmut_24(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalty = None

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


def x__vol_target_weights__mutmut_25(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalty = {t: 1.0 for t in tickers}

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


def x__vol_target_weights__mutmut_26(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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

    for i, a in enumerate(None):
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


def x__vol_target_weights__mutmut_27(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        for b in tickers[i - 1 :]:
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


def x__vol_target_weights__mutmut_28(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        for b in tickers[i + 2 :]:
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


def x__vol_target_weights__mutmut_29(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            c = None
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


def x__vol_target_weights__mutmut_30(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            c = corr_matrix.loc[a, b] if (a in corr_matrix.index or b in corr_matrix.columns) else 0.0
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


def x__vol_target_weights__mutmut_31(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            c = corr_matrix.loc[a, b] if (a not in corr_matrix.index and b in corr_matrix.columns) else 0.0
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


def x__vol_target_weights__mutmut_32(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            c = corr_matrix.loc[a, b] if (a in corr_matrix.index and b not in corr_matrix.columns) else 0.0
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


def x__vol_target_weights__mutmut_33(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            c = corr_matrix.loc[a, b] if (a in corr_matrix.index and b in corr_matrix.columns) else 1.0
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


def x__vol_target_weights__mutmut_34(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            if abs(None) > CORR_THRESHOLD:
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


def x__vol_target_weights__mutmut_35(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
            if abs(c) >= CORR_THRESHOLD:
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


def x__vol_target_weights__mutmut_36(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append(None)
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


def x__vol_target_weights__mutmut_37(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"XXaXX": a, "b": b, "correlation": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_38(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"A": a, "b": b, "correlation": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_39(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "XXbXX": b, "correlation": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_40(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "B": b, "correlation": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_41(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "XXcorrelationXX": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_42(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "CORRELATION": round(float(c), 3)})
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


def x__vol_target_weights__mutmut_43(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(None, 3)})
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


def x__vol_target_weights__mutmut_44(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(float(c), None)})
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


def x__vol_target_weights__mutmut_45(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(3)})
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


def x__vol_target_weights__mutmut_46(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(float(c), )})
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


def x__vol_target_weights__mutmut_47(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(float(None), 3)})
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


def x__vol_target_weights__mutmut_48(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                high_corr_pairs.append({"a": a, "b": b, "correlation": round(float(c), 4)})
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


def x__vol_target_weights__mutmut_49(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = None
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


def x__vol_target_weights__mutmut_50(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = (abs(c) - CORR_THRESHOLD) * (1.0 - CORR_THRESHOLD)
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


def x__vol_target_weights__mutmut_51(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = (abs(c) + CORR_THRESHOLD) / (1.0 - CORR_THRESHOLD)
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


def x__vol_target_weights__mutmut_52(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = (abs(None) - CORR_THRESHOLD) / (1.0 - CORR_THRESHOLD)
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


def x__vol_target_weights__mutmut_53(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = (abs(c) - CORR_THRESHOLD) / (1.0 + CORR_THRESHOLD)
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


def x__vol_target_weights__mutmut_54(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                excess = (abs(c) - CORR_THRESHOLD) / (2.0 - CORR_THRESHOLD)
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


def x__vol_target_weights__mutmut_55(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[a] = excess * 0.5
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


def x__vol_target_weights__mutmut_56(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[a] -= excess * 0.5
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


def x__vol_target_weights__mutmut_57(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[a] += excess / 0.5
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


def x__vol_target_weights__mutmut_58(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[a] += excess * 1.5
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


def x__vol_target_weights__mutmut_59(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[b] = excess * 0.5

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


def x__vol_target_weights__mutmut_60(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[b] -= excess * 0.5

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


def x__vol_target_weights__mutmut_61(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[b] += excess / 0.5

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


def x__vol_target_weights__mutmut_62(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                penalty[b] += excess * 1.5

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


def x__vol_target_weights__mutmut_63(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = None
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


def x__vol_target_weights__mutmut_64(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] / max(0.6, 1.0 - penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_65(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(None, 1.0 - penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_66(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(0.6, None) for t in tickers}
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


def x__vol_target_weights__mutmut_67(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(1.0 - penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_68(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(0.6, ) for t in tickers}
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


def x__vol_target_weights__mutmut_69(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(1.6, 1.0 - penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_70(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(0.6, 1.0 + penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_71(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    penalised_weights = {t: raw_weights[t] * max(0.6, 2.0 - penalty[t]) for t in tickers}
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


def x__vol_target_weights__mutmut_72(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_pen = None
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


def x__vol_target_weights__mutmut_73(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_pen = sum(penalised_weights.values()) and 1.0
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


def x__vol_target_weights__mutmut_74(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_pen = sum(None) or 1.0
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


def x__vol_target_weights__mutmut_75(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_pen = sum(penalised_weights.values()) or 2.0
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


def x__vol_target_weights__mutmut_76(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final_weights = None

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


def x__vol_target_weights__mutmut_77(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final_weights = {t: penalised_weights[t] * total_pen for t in tickers}

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


def x__vol_target_weights__mutmut_78(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    w = None
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


def x__vol_target_weights__mutmut_79(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    w = np.array(None)
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


def x__vol_target_weights__mutmut_80(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    cov = None
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


def x__vol_target_weights__mutmut_81(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    cov = returns_df.cov() / TRADING_DAYS
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


def x__vol_target_weights__mutmut_82(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_var = None
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


def x__vol_target_weights__mutmut_83(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_var = float(None)
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


def x__vol_target_weights__mutmut_84(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = None

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


def x__vol_target_weights__mutmut_85(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(None)

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


def x__vol_target_weights__mutmut_86(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(None))

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


def x__vol_target_weights__mutmut_87(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(max(None, 0)))

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


def x__vol_target_weights__mutmut_88(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(max(port_var, None)))

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


def x__vol_target_weights__mutmut_89(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(max(0)))

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


def x__vol_target_weights__mutmut_90(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(max(port_var, )))

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


def x__vol_target_weights__mutmut_91(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    port_vol = float(np.sqrt(max(port_var, 1)))

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


def x__vol_target_weights__mutmut_92(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = None
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


def x__vol_target_weights__mutmut_93(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = TARGET_VOL * port_vol if port_vol > 1e-6 else 1.0
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


def x__vol_target_weights__mutmut_94(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = TARGET_VOL / port_vol if port_vol >= 1e-6 else 1.0
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


def x__vol_target_weights__mutmut_95(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = TARGET_VOL / port_vol if port_vol > 1.000001 else 1.0
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


def x__vol_target_weights__mutmut_96(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = TARGET_VOL / port_vol if port_vol > 1e-6 else 2.0
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


def x__vol_target_weights__mutmut_97(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = None
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


def x__vol_target_weights__mutmut_98(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = min(None, 2.0)
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


def x__vol_target_weights__mutmut_99(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = min(scale_factor, None)
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


def x__vol_target_weights__mutmut_100(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = min(2.0)
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


def x__vol_target_weights__mutmut_101(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = min(scale_factor, )
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


def x__vol_target_weights__mutmut_102(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scale_factor = min(scale_factor, 3.0)
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


def x__vol_target_weights__mutmut_103(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = None

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


def x__vol_target_weights__mutmut_104(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(None, 0.40) for t in tickers}

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


def x__vol_target_weights__mutmut_105(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(final_weights[t] * scale_factor, None) for t in tickers}

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


def x__vol_target_weights__mutmut_106(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(0.40) for t in tickers}

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


def x__vol_target_weights__mutmut_107(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(final_weights[t] * scale_factor, ) for t in tickers}

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


def x__vol_target_weights__mutmut_108(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(final_weights[t] / scale_factor, 0.40) for t in tickers}

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


def x__vol_target_weights__mutmut_109(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    scaled_weights = {t: min(final_weights[t] * scale_factor, 1.4) for t in tickers}

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


def x__vol_target_weights__mutmut_110(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_scaled = None
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


def x__vol_target_weights__mutmut_111(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_scaled = sum(scaled_weights.values()) and 1.0
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


def x__vol_target_weights__mutmut_112(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_scaled = sum(None) or 1.0
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


def x__vol_target_weights__mutmut_113(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    total_scaled = sum(scaled_weights.values()) or 2.0
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


def x__vol_target_weights__mutmut_114(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = None

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


def x__vol_target_weights__mutmut_115(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(None, 4) for t in tickers}

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


def x__vol_target_weights__mutmut_116(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(scaled_weights[t] / total_scaled, None) for t in tickers}

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


def x__vol_target_weights__mutmut_117(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(4) for t in tickers}

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


def x__vol_target_weights__mutmut_118(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(scaled_weights[t] / total_scaled, ) for t in tickers}

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


def x__vol_target_weights__mutmut_119(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(scaled_weights[t] * total_scaled, 4) for t in tickers}

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


def x__vol_target_weights__mutmut_120(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    final = {t: round(scaled_weights[t] / total_scaled, 5) for t in tickers}

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


def x__vol_target_weights__mutmut_121(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = None

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


def x__vol_target_weights__mutmut_122(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(None, key=lambda x: x[1], reverse=True)

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


def x__vol_target_weights__mutmut_123(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=None, reverse=True)

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


def x__vol_target_weights__mutmut_124(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=lambda x: x[1], reverse=None)

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


def x__vol_target_weights__mutmut_125(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(key=lambda x: x[1], reverse=True)

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


def x__vol_target_weights__mutmut_126(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), reverse=True)

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


def x__vol_target_weights__mutmut_127(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=lambda x: x[1], )

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


def x__vol_target_weights__mutmut_128(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=lambda x: None, reverse=True)

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


def x__vol_target_weights__mutmut_129(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=lambda x: x[2], reverse=True)

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


def x__vol_target_weights__mutmut_130(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
    sorted_assets = sorted(final.items(), key=lambda x: x[1], reverse=False)

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


def x__vol_target_weights__mutmut_131(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "XXtarget_vol_pctXX": round(TARGET_VOL * 100, 1),
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


def x__vol_target_weights__mutmut_132(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "TARGET_VOL_PCT": round(TARGET_VOL * 100, 1),
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


def x__vol_target_weights__mutmut_133(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(None, 1),
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


def x__vol_target_weights__mutmut_134(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(TARGET_VOL * 100, None),
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


def x__vol_target_weights__mutmut_135(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(1),
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


def x__vol_target_weights__mutmut_136(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(TARGET_VOL * 100, ),
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


def x__vol_target_weights__mutmut_137(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(TARGET_VOL / 100, 1),
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


def x__vol_target_weights__mutmut_138(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(TARGET_VOL * 101, 1),
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


def x__vol_target_weights__mutmut_139(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "target_vol_pct": round(TARGET_VOL * 100, 2),
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


def x__vol_target_weights__mutmut_140(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "XXestimated_port_vol_pctXX": round(port_vol * 100, 2),
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


def x__vol_target_weights__mutmut_141(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "ESTIMATED_PORT_VOL_PCT": round(port_vol * 100, 2),
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


def x__vol_target_weights__mutmut_142(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(None, 2),
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


def x__vol_target_weights__mutmut_143(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(port_vol * 100, None),
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


def x__vol_target_weights__mutmut_144(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(2),
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


def x__vol_target_weights__mutmut_145(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(port_vol * 100, ),
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


def x__vol_target_weights__mutmut_146(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(port_vol / 100, 2),
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


def x__vol_target_weights__mutmut_147(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(port_vol * 101, 2),
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


def x__vol_target_weights__mutmut_148(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "estimated_port_vol_pct": round(port_vol * 100, 3),
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


def x__vol_target_weights__mutmut_149(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "XXscale_factorXX": round(scale_factor, 3),
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


def x__vol_target_weights__mutmut_150(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "SCALE_FACTOR": round(scale_factor, 3),
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


def x__vol_target_weights__mutmut_151(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "scale_factor": round(None, 3),
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


def x__vol_target_weights__mutmut_152(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "scale_factor": round(scale_factor, None),
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


def x__vol_target_weights__mutmut_153(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "scale_factor": round(3),
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


def x__vol_target_weights__mutmut_154(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "scale_factor": round(scale_factor, ),
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


def x__vol_target_weights__mutmut_155(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "scale_factor": round(scale_factor, 4),
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


def x__vol_target_weights__mutmut_156(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "XXassetsXX": [
            {
                "ticker": t,
                "weight_pct": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_157(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "ASSETS": [
            {
                "ticker": t,
                "weight_pct": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_158(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "XXtickerXX": t,
                "weight_pct": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_159(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "TICKER": t,
                "weight_pct": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_160(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "XXweight_pctXX": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_161(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "WEIGHT_PCT": round(w * 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_162(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(None, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_163(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(w * 100, None),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_164(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_165(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(w * 100, ),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_166(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(w / 100, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_167(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(w * 101, 2),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_168(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "weight_pct": round(w * 100, 3),
                "annual_vol_pct": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_169(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "XXannual_vol_pctXX": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_170(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "ANNUAL_VOL_PCT": round(vols[t] * 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_171(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(None, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_172(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(vols[t] * 100, None),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_173(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_174(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(vols[t] * 100, ),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_175(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(vols[t] / 100, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_176(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(vols[t] * 101, 2),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_177(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
                "annual_vol_pct": round(vols[t] * 100, 3),
            }
            for t, w in sorted_assets
        ],
        "high_correlation_pairs": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_178(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "XXhigh_correlation_pairsXX": high_corr_pairs,
    }


def x__vol_target_weights__mutmut_179(returns_df: pd.DataFrame) -> dict:
    """
    Compute inverse-vol weights with correlation penalty.
    Returns dict with per-asset weights, vols, correlations above threshold.
    """
    if returns_df.empty or len(returns_df.columns) < 1:
        return {}

    tickers = list(returns_df.columns)

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
        "HIGH_CORRELATION_PAIRS": high_corr_pairs,
    }

mutants_x__vol_target_weights__mutmut['_mutmut_orig'] = x__vol_target_weights__mutmut_orig # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_1'] = x__vol_target_weights__mutmut_1 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_2'] = x__vol_target_weights__mutmut_2 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_3'] = x__vol_target_weights__mutmut_3 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_4'] = x__vol_target_weights__mutmut_4 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_5'] = x__vol_target_weights__mutmut_5 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_6'] = x__vol_target_weights__mutmut_6 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_7'] = x__vol_target_weights__mutmut_7 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_8'] = x__vol_target_weights__mutmut_8 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_9'] = x__vol_target_weights__mutmut_9 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_10'] = x__vol_target_weights__mutmut_10 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_11'] = x__vol_target_weights__mutmut_11 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_12'] = x__vol_target_weights__mutmut_12 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_13'] = x__vol_target_weights__mutmut_13 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_14'] = x__vol_target_weights__mutmut_14 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_15'] = x__vol_target_weights__mutmut_15 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_16'] = x__vol_target_weights__mutmut_16 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_17'] = x__vol_target_weights__mutmut_17 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_18'] = x__vol_target_weights__mutmut_18 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_19'] = x__vol_target_weights__mutmut_19 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_20'] = x__vol_target_weights__mutmut_20 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_21'] = x__vol_target_weights__mutmut_21 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_22'] = x__vol_target_weights__mutmut_22 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_23'] = x__vol_target_weights__mutmut_23 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_24'] = x__vol_target_weights__mutmut_24 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_25'] = x__vol_target_weights__mutmut_25 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_26'] = x__vol_target_weights__mutmut_26 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_27'] = x__vol_target_weights__mutmut_27 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_28'] = x__vol_target_weights__mutmut_28 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_29'] = x__vol_target_weights__mutmut_29 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_30'] = x__vol_target_weights__mutmut_30 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_31'] = x__vol_target_weights__mutmut_31 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_32'] = x__vol_target_weights__mutmut_32 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_33'] = x__vol_target_weights__mutmut_33 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_34'] = x__vol_target_weights__mutmut_34 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_35'] = x__vol_target_weights__mutmut_35 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_36'] = x__vol_target_weights__mutmut_36 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_37'] = x__vol_target_weights__mutmut_37 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_38'] = x__vol_target_weights__mutmut_38 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_39'] = x__vol_target_weights__mutmut_39 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_40'] = x__vol_target_weights__mutmut_40 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_41'] = x__vol_target_weights__mutmut_41 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_42'] = x__vol_target_weights__mutmut_42 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_43'] = x__vol_target_weights__mutmut_43 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_44'] = x__vol_target_weights__mutmut_44 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_45'] = x__vol_target_weights__mutmut_45 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_46'] = x__vol_target_weights__mutmut_46 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_47'] = x__vol_target_weights__mutmut_47 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_48'] = x__vol_target_weights__mutmut_48 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_49'] = x__vol_target_weights__mutmut_49 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_50'] = x__vol_target_weights__mutmut_50 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_51'] = x__vol_target_weights__mutmut_51 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_52'] = x__vol_target_weights__mutmut_52 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_53'] = x__vol_target_weights__mutmut_53 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_54'] = x__vol_target_weights__mutmut_54 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_55'] = x__vol_target_weights__mutmut_55 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_56'] = x__vol_target_weights__mutmut_56 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_57'] = x__vol_target_weights__mutmut_57 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_58'] = x__vol_target_weights__mutmut_58 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_59'] = x__vol_target_weights__mutmut_59 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_60'] = x__vol_target_weights__mutmut_60 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_61'] = x__vol_target_weights__mutmut_61 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_62'] = x__vol_target_weights__mutmut_62 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_63'] = x__vol_target_weights__mutmut_63 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_64'] = x__vol_target_weights__mutmut_64 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_65'] = x__vol_target_weights__mutmut_65 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_66'] = x__vol_target_weights__mutmut_66 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_67'] = x__vol_target_weights__mutmut_67 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_68'] = x__vol_target_weights__mutmut_68 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_69'] = x__vol_target_weights__mutmut_69 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_70'] = x__vol_target_weights__mutmut_70 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_71'] = x__vol_target_weights__mutmut_71 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_72'] = x__vol_target_weights__mutmut_72 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_73'] = x__vol_target_weights__mutmut_73 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_74'] = x__vol_target_weights__mutmut_74 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_75'] = x__vol_target_weights__mutmut_75 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_76'] = x__vol_target_weights__mutmut_76 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_77'] = x__vol_target_weights__mutmut_77 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_78'] = x__vol_target_weights__mutmut_78 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_79'] = x__vol_target_weights__mutmut_79 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_80'] = x__vol_target_weights__mutmut_80 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_81'] = x__vol_target_weights__mutmut_81 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_82'] = x__vol_target_weights__mutmut_82 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_83'] = x__vol_target_weights__mutmut_83 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_84'] = x__vol_target_weights__mutmut_84 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_85'] = x__vol_target_weights__mutmut_85 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_86'] = x__vol_target_weights__mutmut_86 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_87'] = x__vol_target_weights__mutmut_87 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_88'] = x__vol_target_weights__mutmut_88 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_89'] = x__vol_target_weights__mutmut_89 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_90'] = x__vol_target_weights__mutmut_90 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_91'] = x__vol_target_weights__mutmut_91 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_92'] = x__vol_target_weights__mutmut_92 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_93'] = x__vol_target_weights__mutmut_93 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_94'] = x__vol_target_weights__mutmut_94 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_95'] = x__vol_target_weights__mutmut_95 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_96'] = x__vol_target_weights__mutmut_96 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_97'] = x__vol_target_weights__mutmut_97 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_98'] = x__vol_target_weights__mutmut_98 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_99'] = x__vol_target_weights__mutmut_99 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_100'] = x__vol_target_weights__mutmut_100 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_101'] = x__vol_target_weights__mutmut_101 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_102'] = x__vol_target_weights__mutmut_102 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_103'] = x__vol_target_weights__mutmut_103 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_104'] = x__vol_target_weights__mutmut_104 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_105'] = x__vol_target_weights__mutmut_105 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_106'] = x__vol_target_weights__mutmut_106 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_107'] = x__vol_target_weights__mutmut_107 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_108'] = x__vol_target_weights__mutmut_108 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_109'] = x__vol_target_weights__mutmut_109 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_110'] = x__vol_target_weights__mutmut_110 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_111'] = x__vol_target_weights__mutmut_111 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_112'] = x__vol_target_weights__mutmut_112 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_113'] = x__vol_target_weights__mutmut_113 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_114'] = x__vol_target_weights__mutmut_114 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_115'] = x__vol_target_weights__mutmut_115 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_116'] = x__vol_target_weights__mutmut_116 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_117'] = x__vol_target_weights__mutmut_117 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_118'] = x__vol_target_weights__mutmut_118 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_119'] = x__vol_target_weights__mutmut_119 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_120'] = x__vol_target_weights__mutmut_120 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_121'] = x__vol_target_weights__mutmut_121 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_122'] = x__vol_target_weights__mutmut_122 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_123'] = x__vol_target_weights__mutmut_123 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_124'] = x__vol_target_weights__mutmut_124 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_125'] = x__vol_target_weights__mutmut_125 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_126'] = x__vol_target_weights__mutmut_126 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_127'] = x__vol_target_weights__mutmut_127 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_128'] = x__vol_target_weights__mutmut_128 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_129'] = x__vol_target_weights__mutmut_129 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_130'] = x__vol_target_weights__mutmut_130 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_131'] = x__vol_target_weights__mutmut_131 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_132'] = x__vol_target_weights__mutmut_132 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_133'] = x__vol_target_weights__mutmut_133 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_134'] = x__vol_target_weights__mutmut_134 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_135'] = x__vol_target_weights__mutmut_135 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_136'] = x__vol_target_weights__mutmut_136 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_137'] = x__vol_target_weights__mutmut_137 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_138'] = x__vol_target_weights__mutmut_138 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_139'] = x__vol_target_weights__mutmut_139 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_140'] = x__vol_target_weights__mutmut_140 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_141'] = x__vol_target_weights__mutmut_141 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_142'] = x__vol_target_weights__mutmut_142 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_143'] = x__vol_target_weights__mutmut_143 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_144'] = x__vol_target_weights__mutmut_144 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_145'] = x__vol_target_weights__mutmut_145 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_146'] = x__vol_target_weights__mutmut_146 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_147'] = x__vol_target_weights__mutmut_147 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_148'] = x__vol_target_weights__mutmut_148 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_149'] = x__vol_target_weights__mutmut_149 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_150'] = x__vol_target_weights__mutmut_150 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_151'] = x__vol_target_weights__mutmut_151 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_152'] = x__vol_target_weights__mutmut_152 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_153'] = x__vol_target_weights__mutmut_153 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_154'] = x__vol_target_weights__mutmut_154 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_155'] = x__vol_target_weights__mutmut_155 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_156'] = x__vol_target_weights__mutmut_156 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_157'] = x__vol_target_weights__mutmut_157 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_158'] = x__vol_target_weights__mutmut_158 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_159'] = x__vol_target_weights__mutmut_159 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_160'] = x__vol_target_weights__mutmut_160 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_161'] = x__vol_target_weights__mutmut_161 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_162'] = x__vol_target_weights__mutmut_162 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_163'] = x__vol_target_weights__mutmut_163 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_164'] = x__vol_target_weights__mutmut_164 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_165'] = x__vol_target_weights__mutmut_165 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_166'] = x__vol_target_weights__mutmut_166 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_167'] = x__vol_target_weights__mutmut_167 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_168'] = x__vol_target_weights__mutmut_168 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_169'] = x__vol_target_weights__mutmut_169 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_170'] = x__vol_target_weights__mutmut_170 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_171'] = x__vol_target_weights__mutmut_171 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_172'] = x__vol_target_weights__mutmut_172 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_173'] = x__vol_target_weights__mutmut_173 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_174'] = x__vol_target_weights__mutmut_174 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_175'] = x__vol_target_weights__mutmut_175 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_176'] = x__vol_target_weights__mutmut_176 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_177'] = x__vol_target_weights__mutmut_177 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_178'] = x__vol_target_weights__mutmut_178 # type: ignore # mutmut generated
mutants_x__vol_target_weights__mutmut['x__vol_target_weights__mutmut_179'] = x__vol_target_weights__mutmut_179 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_volatility_target_weights__mutmut)
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_orig(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_1(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_2(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = None

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_3(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["XXSPYXX", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_4(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["spy", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_5(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "XXQQQXX", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_6(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "qqq", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_7(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "XXIWMXX", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_8(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "iwm", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_9(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "XXGLDXX", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_10(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "gld", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_11(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "XXTLTXX", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_12(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "tlt", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_13(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "XXHYGXX", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_14(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "hyg", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_15(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "XXDXYXX", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_16(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "dxy", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_17(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XXXLEXX", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_18(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "xle", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_19(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XXXLKXX", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_20(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "xlk", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_21(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XXXLFXX"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_22(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "xlf"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_23(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = None
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_24(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.lower() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_25(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) <= 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_26(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 3:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_27(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"XXerrorXX": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_28(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"ERROR": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_29(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "XXAt least 2 tickers requiredXX"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_30(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "at least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_31(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "AT LEAST 2 TICKERS REQUIRED"}

    try:
        returns_df = await _fetch_returns(tickers)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_32(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = None
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_33(tickers: Optional[list[str]] = None) -> dict:
    """
    Public entrypoint. If no tickers provided, uses a default cross-asset basket.
    """
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "GLD", "TLT", "HYG", "DXY", "XLE", "XLK", "XLF"]

    tickers = [t.upper() for t in tickers if t.strip()]
    if len(tickers) < 2:
        return {"error": "At least 2 tickers required"}

    try:
        returns_df = await _fetch_returns(None)
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_34(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"XXerrorXX": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_35(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"ERROR": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_36(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "XXCould not fetch return data for the provided tickersXX"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_37(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_38(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "COULD NOT FETCH RETURN DATA FOR THE PROVIDED TICKERS"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_39(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = None
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_40(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(None, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_41(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, None)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_42(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_43(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, )
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_44(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = None
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_45(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["XXtickers_requestedXX"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_46(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["TICKERS_REQUESTED"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_47(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = None
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_48(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["XXtickers_resolvedXX"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_49(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["TICKERS_RESOLVED"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_50(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(None)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_51(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(None, exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_52(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=None)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_53(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(exc_info=True)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_54(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", )
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_55(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=False)
        return {"error": str(e)}


async def x_get_volatility_target_weights__mutmut_56(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"XXerrorXX": str(e)}


async def x_get_volatility_target_weights__mutmut_57(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"ERROR": str(e)}


async def x_get_volatility_target_weights__mutmut_58(tickers: Optional[list[str]] = None) -> dict:
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
        if returns_df.empty:
            return {"error": "Could not fetch return data for the provided tickers"}
        result = await asyncio.to_thread(_vol_target_weights, returns_df)
        result["tickers_requested"] = tickers
        result["tickers_resolved"] = list(returns_df.columns)
        return result
    except Exception as e:
        log.error(f"[vol_target] Error: {e}", exc_info=True)
        return {"error": str(None)}

mutants_x_get_volatility_target_weights__mutmut['_mutmut_orig'] = x_get_volatility_target_weights__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_1'] = x_get_volatility_target_weights__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_2'] = x_get_volatility_target_weights__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_3'] = x_get_volatility_target_weights__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_4'] = x_get_volatility_target_weights__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_5'] = x_get_volatility_target_weights__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_6'] = x_get_volatility_target_weights__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_7'] = x_get_volatility_target_weights__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_8'] = x_get_volatility_target_weights__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_9'] = x_get_volatility_target_weights__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_10'] = x_get_volatility_target_weights__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_11'] = x_get_volatility_target_weights__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_12'] = x_get_volatility_target_weights__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_13'] = x_get_volatility_target_weights__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_14'] = x_get_volatility_target_weights__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_15'] = x_get_volatility_target_weights__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_16'] = x_get_volatility_target_weights__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_17'] = x_get_volatility_target_weights__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_18'] = x_get_volatility_target_weights__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_19'] = x_get_volatility_target_weights__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_20'] = x_get_volatility_target_weights__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_21'] = x_get_volatility_target_weights__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_22'] = x_get_volatility_target_weights__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_23'] = x_get_volatility_target_weights__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_24'] = x_get_volatility_target_weights__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_25'] = x_get_volatility_target_weights__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_26'] = x_get_volatility_target_weights__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_27'] = x_get_volatility_target_weights__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_28'] = x_get_volatility_target_weights__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_29'] = x_get_volatility_target_weights__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_30'] = x_get_volatility_target_weights__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_31'] = x_get_volatility_target_weights__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_32'] = x_get_volatility_target_weights__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_33'] = x_get_volatility_target_weights__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_34'] = x_get_volatility_target_weights__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_35'] = x_get_volatility_target_weights__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_36'] = x_get_volatility_target_weights__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_37'] = x_get_volatility_target_weights__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_38'] = x_get_volatility_target_weights__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_39'] = x_get_volatility_target_weights__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_40'] = x_get_volatility_target_weights__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_41'] = x_get_volatility_target_weights__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_42'] = x_get_volatility_target_weights__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_43'] = x_get_volatility_target_weights__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_44'] = x_get_volatility_target_weights__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_45'] = x_get_volatility_target_weights__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_46'] = x_get_volatility_target_weights__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_47'] = x_get_volatility_target_weights__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_48'] = x_get_volatility_target_weights__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_49'] = x_get_volatility_target_weights__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_50'] = x_get_volatility_target_weights__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_51'] = x_get_volatility_target_weights__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_52'] = x_get_volatility_target_weights__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_53'] = x_get_volatility_target_weights__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_54'] = x_get_volatility_target_weights__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_55'] = x_get_volatility_target_weights__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_56'] = x_get_volatility_target_weights__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_57'] = x_get_volatility_target_weights__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_volatility_target_weights__mutmut['x_get_volatility_target_weights__mutmut_58'] = x_get_volatility_target_weights__mutmut_58 # type: ignore # mutmut generated
