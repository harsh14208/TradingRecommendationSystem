"""
Market breadth: % of a representative S&P 500 basket trading above their SMA50 and SMA200.
Uses yfinance batch download — no API key, no cost. Cached 2 hours (breadth is slow-moving).

Interpretation (contrarian at extremes, momentum in the middle):
  pct_above_200d >= 70% → broad participation, bullish  (+10)
  pct_above_200d >= 55% → healthy market, mild bullish   (+5)
  pct_above_200d <= 30% → market deterioration, bearish  (-10)
  pct_above_200d <= 45% → weakening, mild bearish         (-5)
  otherwise             → neutral                          (0)
"""
import asyncio
import time

import yfinance as yf

# 50-stock representative S&P 500 basket, 5 per sector
_BASKET = [
    # Technology
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    # Financials
    "JPM", "BAC", "GS", "V", "MA",
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "PFE",
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE",
    # Consumer Staples
    "WMT", "COST", "PG", "KO", "PEP",
    # Industrials
    "CAT", "HON", "GE", "UPS", "RTX",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG",
    # Materials
    "LIN", "APD", "SHW", "FCX", "NEM",
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP",
    # Real Estate
    "AMT", "PLD", "EQIX", "PSA", "O",
]

_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 7200  # 2 hours


def _compute_breadth() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if raw is None or raw.empty:
            return None

        closes = raw.get("Close") if isinstance(raw.columns, object) and "Close" in raw else None
        if closes is None:
            return None

        above_50 = above_200 = counted = 0
        for ticker in _BASKET:
            try:
                col = closes[ticker] if ticker in closes.columns else None
                if col is None:
                    continue
                col = col.dropna()
                if len(col) < 50:
                    continue
                price = float(col.iloc[-1])
                if len(col) >= 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50  = round(above_50  / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish",  10
        elif pct_200 >= 55:
            signal, b_score = "bullish",   5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish",  -5
        else:
            signal, b_score = "neutral",   0

        return {
            "pct_above_50d":  pct_50,
            "pct_above_200d": pct_200,
            "signal":  signal,
            "score":   b_score,
            "n":       counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


async def get_market_breadth() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"]   = now
    return result or _cache.get("data")
