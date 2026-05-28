"""
Cointegration-based pairs trading signals.

For each pre-defined pair, computes the OLS-regression spread, z-scores it
against a 90-day history, and returns a bullish/bearish score when the spread
diverges beyond ±2σ and the rolling correlation is ≥ 0.70.

No external ML deps — uses numpy only.
"""

import asyncio
import time

import numpy as np

from services.market_data import get_history

# ── Known cointegrated pairs (sector-matched, economically linked) ──────────
PAIRS: list[tuple[str, str]] = [
    # Semiconductors
    ("NVDA", "AMD"),
    ("NVDA", "INTC"),
    ("AVGO", "QCOM"),
    # Big Tech / Cloud
    ("MSFT", "GOOGL"),
    ("MSFT", "AAPL"),
    ("AMZN", "GOOGL"),
    # Social / Consumer Internet
    ("META", "SNAP"),
    # Finance
    ("JPM", "BAC"),
    ("GS", "MS"),
    ("V", "MA"),
    # Energy
    ("XOM", "CVX"),
    # EV
    ("TSLA", "RIVN"),
    # Retail
    ("WMT", "TGT"),
    # Streaming / Entertainment
    ("NFLX", "DIS"),
]

# In-memory cache: {cache_key: (timestamp, result_dict)}
_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 7200  # 2 hours — pairs relationships move slowly


async def get_pairs_signals(watchlist: list[str]) -> dict[str, dict]:
    """
    Returns {ticker: {score, pair_ticker, zscore, correlation, direction}}
    for every watchlist ticker that appears in a cointegrated pair with a
    current spread divergence exceeding ±2σ.
    """
    cache_key = ",".join(sorted(watchlist))
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < _CACHE_TTL:
        return cached[1]

    # Only analyse pairs where at least one leg is in the watchlist
    relevant = [(a, b) for a, b in PAIRS if a in watchlist or b in watchlist]
    if not relevant:
        return {}

    results: dict[str, dict] = {}

    async def _analyse_pair(ticker_a: str, ticker_b: str) -> None:
        try:
            df_a, df_b = await asyncio.gather(
                get_history(ticker_a, period="6mo", interval="1d"),
                get_history(ticker_b, period="6mo", interval="1d"),
            )
            if df_a is None or df_b is None:
                return
            if len(df_a) < 60 or len(df_b) < 60:
                return

            ca = df_a["Close"].astype(float)
            cb = df_b["Close"].astype(float)

            # Align on common trading dates
            common = ca.index.intersection(cb.index)
            if len(common) < 50:
                return

            va = ca.loc[common].values
            vb = cb.loc[common].values

            # ── OLS hedge ratio β (numpy only) ──────────────────────────────
            # spread(t) = A(t) − β·B(t)
            beta = np.cov(va, vb)[0, 1] / max(np.var(vb), 1e-10)
            spread = va - beta * vb

            # Use first 80% as "training" window to compute mean/std,
            # z-score the most recent value against that history.
            cut = max(30, int(len(spread) * 0.80))
            mu = float(np.mean(spread[:cut]))
            sig = float(np.std(spread[:cut]))
            if sig < 1e-8:
                return

            zscore = (spread[-1] - mu) / sig

            # Rolling 60-day Pearson correlation
            n_roll = min(60, len(va))
            corr = float(np.corrcoef(va[-n_roll:], vb[-n_roll:])[0, 1])

            # Only act on strongly correlated pairs with significant divergence
            if abs(corr) < 0.70 or abs(zscore) < 2.0:
                return

            # ── Directional scores ──────────────────────────────────────────
            # z < -2  →  spread too low  →  A cheap vs B  →  BUY A, SELL B
            # z > +2  →  spread too high →  A dear vs B   →  SELL A, BUY B
            raw_score = float(np.clip(abs(zscore) * 4, 5, 16))

            for target, sign in [(ticker_a, -zscore), (ticker_b, zscore)]:
                if target not in watchlist:
                    continue
                direction_score = raw_score if sign > 0 else -raw_score
                other = ticker_b if target == ticker_a else ticker_a
                candidate = {
                    "score": round(direction_score, 1),
                    "pair_ticker": other,
                    "zscore": round(float(zscore), 2),
                    "correlation": round(corr, 3),
                    "direction": "undervalued" if direction_score > 0 else "overvalued",
                    "beta": round(float(beta), 4),
                }
                # Keep the most extreme signal if two pairs compete for the same ticker
                existing = results.get(target)
                if not existing or abs(direction_score) > abs(existing["score"]):
                    results[target] = candidate

        except Exception:
            pass  # non-critical — degrade gracefully

    await asyncio.gather(*[_analyse_pair(a, b) for a, b in relevant])

    _cache[cache_key] = (time.time(), results)
    return results
