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
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
    # Financials
    "JPM",
    "BAC",
    "GS",
    "V",
    "MA",
    # Healthcare
    "UNH",
    "JNJ",
    "LLY",
    "ABBV",
    "PFE",
    # Consumer Discretionary
    "AMZN",
    "TSLA",
    "HD",
    "MCD",
    "NKE",
    # Consumer Staples
    "WMT",
    "COST",
    "PG",
    "KO",
    "PEP",
    # Industrials
    "CAT",
    "HON",
    "GE",
    "UPS",
    "RTX",
    # Energy
    "XOM",
    "CVX",
    "COP",
    "SLB",
    "EOG",
    # Materials
    "LIN",
    "APD",
    "SHW",
    "FCX",
    "NEM",
    # Utilities
    "NEE",
    "DUK",
    "SO",
    "D",
    "AEP",
    # Real Estate
    "AMT",
    "PLD",
    "EQIX",
    "PSA",
    "O",
]

_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 7200  # 2 hours


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__compute_breadth__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__compute_breadth__mutmut)
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_orig() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_1() -> dict | None:
    try:
        raw = None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_2() -> dict | None:
    try:
        raw = yf.download(
            None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_3() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period=None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_4() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval=None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_5() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_6() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_7() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=None,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_8() -> dict | None:
    try:
        raw = yf.download(
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_9() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_10() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_11() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_12() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_13() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_14() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="XX1yXX",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_15() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1Y",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_16() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="XX1dXX",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_17() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1D",
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_18() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=False,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_19() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=True,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_20() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_21() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if raw is None and raw.empty:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_22() -> dict | None:
    try:
        raw = yf.download(
            _BASKET,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if raw is not None or raw.empty:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_23() -> dict | None:
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

        closes = None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_24() -> dict | None:
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

        closes = raw.get(None) if isinstance(raw.columns, object) and "Close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_25() -> dict | None:
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

        closes = raw.get("XXCloseXX") if isinstance(raw.columns, object) and "Close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_26() -> dict | None:
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

        closes = raw.get("close") if isinstance(raw.columns, object) and "Close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_27() -> dict | None:
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

        closes = raw.get("CLOSE") if isinstance(raw.columns, object) and "Close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_28() -> dict | None:
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

        closes = raw.get("Close") if isinstance(raw.columns, object) or "Close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_29() -> dict | None:
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

        closes = raw.get("Close") if isinstance(raw.columns, object) and "XXCloseXX" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_30() -> dict | None:
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

        closes = raw.get("Close") if isinstance(raw.columns, object) and "close" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_31() -> dict | None:
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

        closes = raw.get("Close") if isinstance(raw.columns, object) and "CLOSE" in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_32() -> dict | None:
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

        closes = raw.get("Close") if isinstance(raw.columns, object) and "Close" not in raw else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_33() -> dict | None:
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
        if closes is not None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_34() -> dict | None:
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

        above_50 = above_200 = counted = None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_35() -> dict | None:
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

        above_50 = above_200 = counted = 1
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_36() -> dict | None:
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
                col = None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_37() -> dict | None:
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
                col = closes[ticker] if ticker not in closes.columns else None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_38() -> dict | None:
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
                if col is not None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_39() -> dict | None:
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
                    break
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_40() -> dict | None:
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
                col = None
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_41() -> dict | None:
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
                if len(col) <= 50:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_42() -> dict | None:
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
                if len(col) < 51:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_43() -> dict | None:
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
                    break
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_44() -> dict | None:
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
                price = None
                if len(col) >= 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_45() -> dict | None:
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
                price = float(None)
                if len(col) >= 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_46() -> dict | None:
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
                price = float(col.iloc[+1])
                if len(col) >= 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_47() -> dict | None:
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
                price = float(col.iloc[-2])
                if len(col) >= 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_48() -> dict | None:
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
                if len(col) > 50:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_49() -> dict | None:
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
                if len(col) >= 51:
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_50() -> dict | None:
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
                    above_50 = int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_51() -> dict | None:
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
                    above_50 -= int(price > float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_52() -> dict | None:
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
                    above_50 += int(None)
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_53() -> dict | None:
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
                    above_50 += int(price >= float(col.rolling(50).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_54() -> dict | None:
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
                    above_50 += int(price > float(None))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_55() -> dict | None:
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
                    above_50 += int(price > float(col.rolling(None).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_56() -> dict | None:
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
                    above_50 += int(price > float(col.rolling(51).mean().iloc[-1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_57() -> dict | None:
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
                    above_50 += int(price > float(col.rolling(50).mean().iloc[+1]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_58() -> dict | None:
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
                    above_50 += int(price > float(col.rolling(50).mean().iloc[-2]))
                if len(col) >= 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_59() -> dict | None:
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
                if len(col) > 200:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_60() -> dict | None:
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
                if len(col) >= 201:
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_61() -> dict | None:
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
                    above_200 = int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_62() -> dict | None:
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
                    above_200 -= int(price > float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_63() -> dict | None:
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
                    above_200 += int(None)
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_64() -> dict | None:
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
                    above_200 += int(price >= float(col.rolling(200).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_65() -> dict | None:
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
                    above_200 += int(price > float(None))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_66() -> dict | None:
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
                    above_200 += int(price > float(col.rolling(None).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_67() -> dict | None:
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
                    above_200 += int(price > float(col.rolling(201).mean().iloc[-1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_68() -> dict | None:
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
                    above_200 += int(price > float(col.rolling(200).mean().iloc[+1]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_69() -> dict | None:
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
                    above_200 += int(price > float(col.rolling(200).mean().iloc[-2]))
                counted += 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_70() -> dict | None:
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
                counted = 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_71() -> dict | None:
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
                counted -= 1
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_72() -> dict | None:
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
                counted += 2
            except Exception:
                continue

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_73() -> dict | None:
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
                break

        if counted < 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_74() -> dict | None:
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

        if counted <= 10:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_75() -> dict | None:
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

        if counted < 11:
            return None

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_76() -> dict | None:
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

        pct_50 = None
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_77() -> dict | None:
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

        pct_50 = round(None, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_78() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, None)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_79() -> dict | None:
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

        pct_50 = round(1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_80() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, )
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_81() -> dict | None:
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

        pct_50 = round(above_50 / counted / 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_82() -> dict | None:
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

        pct_50 = round(above_50 * counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_83() -> dict | None:
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

        pct_50 = round(above_50 / counted * 101, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_84() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 2)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_85() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = None

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_86() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(None, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_87() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, None)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_88() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_89() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, )

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_90() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted / 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_91() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 * counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_92() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 101, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_93() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 2)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_94() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 > 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_95() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 71:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_96() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = None
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_97() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "XXbullishXX", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_98() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "BULLISH", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_99() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 11
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_100() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 > 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_101() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 56:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_102() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = None
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_103() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "XXbullishXX", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_104() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "BULLISH", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_105() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 6
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_106() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 < 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_107() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 31:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_108() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = None
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_109() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "XXbearishXX", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_110() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "BEARISH", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_111() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", +10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_112() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -11
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_113() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 < 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_114() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 46:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_115() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = None
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_116() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "XXbearishXX", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_117() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "BEARISH", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_118() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", +5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_119() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -6
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_120() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = None

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_121() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "XXneutralXX", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_122() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "NEUTRAL", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_123() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 1

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_124() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "XXpct_above_50dXX": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_125() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "PCT_ABOVE_50D": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_126() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "XXpct_above_200dXX": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_127() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "PCT_ABOVE_200D": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_128() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "XXsignalXX": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_129() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "SIGNAL": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_130() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "XXscoreXX": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_131() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "SCORE": b_score,
            "n": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_132() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "XXnXX": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_133() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "N": counted,
        }
    except Exception as e:
        print(f"[breadth] {e}")
        return None


def x__compute_breadth__mutmut_134() -> dict | None:
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

        pct_50 = round(above_50 / counted * 100, 1)
        pct_200 = round(above_200 / counted * 100, 1)

        if pct_200 >= 70:
            signal, b_score = "bullish", 10
        elif pct_200 >= 55:
            signal, b_score = "bullish", 5
        elif pct_200 <= 30:
            signal, b_score = "bearish", -10
        elif pct_200 <= 45:
            signal, b_score = "bearish", -5
        else:
            signal, b_score = "neutral", 0

        return {
            "pct_above_50d": pct_50,
            "pct_above_200d": pct_200,
            "signal": signal,
            "score": b_score,
            "n": counted,
        }
    except Exception as e:
        print(None)
        return None

mutants_x__compute_breadth__mutmut['_mutmut_orig'] = x__compute_breadth__mutmut_orig # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_1'] = x__compute_breadth__mutmut_1 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_2'] = x__compute_breadth__mutmut_2 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_3'] = x__compute_breadth__mutmut_3 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_4'] = x__compute_breadth__mutmut_4 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_5'] = x__compute_breadth__mutmut_5 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_6'] = x__compute_breadth__mutmut_6 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_7'] = x__compute_breadth__mutmut_7 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_8'] = x__compute_breadth__mutmut_8 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_9'] = x__compute_breadth__mutmut_9 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_10'] = x__compute_breadth__mutmut_10 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_11'] = x__compute_breadth__mutmut_11 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_12'] = x__compute_breadth__mutmut_12 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_13'] = x__compute_breadth__mutmut_13 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_14'] = x__compute_breadth__mutmut_14 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_15'] = x__compute_breadth__mutmut_15 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_16'] = x__compute_breadth__mutmut_16 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_17'] = x__compute_breadth__mutmut_17 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_18'] = x__compute_breadth__mutmut_18 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_19'] = x__compute_breadth__mutmut_19 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_20'] = x__compute_breadth__mutmut_20 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_21'] = x__compute_breadth__mutmut_21 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_22'] = x__compute_breadth__mutmut_22 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_23'] = x__compute_breadth__mutmut_23 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_24'] = x__compute_breadth__mutmut_24 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_25'] = x__compute_breadth__mutmut_25 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_26'] = x__compute_breadth__mutmut_26 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_27'] = x__compute_breadth__mutmut_27 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_28'] = x__compute_breadth__mutmut_28 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_29'] = x__compute_breadth__mutmut_29 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_30'] = x__compute_breadth__mutmut_30 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_31'] = x__compute_breadth__mutmut_31 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_32'] = x__compute_breadth__mutmut_32 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_33'] = x__compute_breadth__mutmut_33 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_34'] = x__compute_breadth__mutmut_34 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_35'] = x__compute_breadth__mutmut_35 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_36'] = x__compute_breadth__mutmut_36 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_37'] = x__compute_breadth__mutmut_37 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_38'] = x__compute_breadth__mutmut_38 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_39'] = x__compute_breadth__mutmut_39 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_40'] = x__compute_breadth__mutmut_40 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_41'] = x__compute_breadth__mutmut_41 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_42'] = x__compute_breadth__mutmut_42 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_43'] = x__compute_breadth__mutmut_43 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_44'] = x__compute_breadth__mutmut_44 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_45'] = x__compute_breadth__mutmut_45 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_46'] = x__compute_breadth__mutmut_46 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_47'] = x__compute_breadth__mutmut_47 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_48'] = x__compute_breadth__mutmut_48 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_49'] = x__compute_breadth__mutmut_49 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_50'] = x__compute_breadth__mutmut_50 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_51'] = x__compute_breadth__mutmut_51 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_52'] = x__compute_breadth__mutmut_52 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_53'] = x__compute_breadth__mutmut_53 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_54'] = x__compute_breadth__mutmut_54 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_55'] = x__compute_breadth__mutmut_55 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_56'] = x__compute_breadth__mutmut_56 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_57'] = x__compute_breadth__mutmut_57 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_58'] = x__compute_breadth__mutmut_58 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_59'] = x__compute_breadth__mutmut_59 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_60'] = x__compute_breadth__mutmut_60 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_61'] = x__compute_breadth__mutmut_61 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_62'] = x__compute_breadth__mutmut_62 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_63'] = x__compute_breadth__mutmut_63 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_64'] = x__compute_breadth__mutmut_64 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_65'] = x__compute_breadth__mutmut_65 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_66'] = x__compute_breadth__mutmut_66 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_67'] = x__compute_breadth__mutmut_67 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_68'] = x__compute_breadth__mutmut_68 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_69'] = x__compute_breadth__mutmut_69 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_70'] = x__compute_breadth__mutmut_70 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_71'] = x__compute_breadth__mutmut_71 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_72'] = x__compute_breadth__mutmut_72 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_73'] = x__compute_breadth__mutmut_73 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_74'] = x__compute_breadth__mutmut_74 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_75'] = x__compute_breadth__mutmut_75 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_76'] = x__compute_breadth__mutmut_76 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_77'] = x__compute_breadth__mutmut_77 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_78'] = x__compute_breadth__mutmut_78 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_79'] = x__compute_breadth__mutmut_79 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_80'] = x__compute_breadth__mutmut_80 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_81'] = x__compute_breadth__mutmut_81 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_82'] = x__compute_breadth__mutmut_82 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_83'] = x__compute_breadth__mutmut_83 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_84'] = x__compute_breadth__mutmut_84 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_85'] = x__compute_breadth__mutmut_85 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_86'] = x__compute_breadth__mutmut_86 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_87'] = x__compute_breadth__mutmut_87 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_88'] = x__compute_breadth__mutmut_88 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_89'] = x__compute_breadth__mutmut_89 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_90'] = x__compute_breadth__mutmut_90 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_91'] = x__compute_breadth__mutmut_91 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_92'] = x__compute_breadth__mutmut_92 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_93'] = x__compute_breadth__mutmut_93 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_94'] = x__compute_breadth__mutmut_94 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_95'] = x__compute_breadth__mutmut_95 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_96'] = x__compute_breadth__mutmut_96 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_97'] = x__compute_breadth__mutmut_97 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_98'] = x__compute_breadth__mutmut_98 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_99'] = x__compute_breadth__mutmut_99 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_100'] = x__compute_breadth__mutmut_100 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_101'] = x__compute_breadth__mutmut_101 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_102'] = x__compute_breadth__mutmut_102 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_103'] = x__compute_breadth__mutmut_103 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_104'] = x__compute_breadth__mutmut_104 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_105'] = x__compute_breadth__mutmut_105 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_106'] = x__compute_breadth__mutmut_106 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_107'] = x__compute_breadth__mutmut_107 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_108'] = x__compute_breadth__mutmut_108 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_109'] = x__compute_breadth__mutmut_109 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_110'] = x__compute_breadth__mutmut_110 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_111'] = x__compute_breadth__mutmut_111 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_112'] = x__compute_breadth__mutmut_112 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_113'] = x__compute_breadth__mutmut_113 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_114'] = x__compute_breadth__mutmut_114 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_115'] = x__compute_breadth__mutmut_115 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_116'] = x__compute_breadth__mutmut_116 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_117'] = x__compute_breadth__mutmut_117 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_118'] = x__compute_breadth__mutmut_118 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_119'] = x__compute_breadth__mutmut_119 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_120'] = x__compute_breadth__mutmut_120 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_121'] = x__compute_breadth__mutmut_121 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_122'] = x__compute_breadth__mutmut_122 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_123'] = x__compute_breadth__mutmut_123 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_124'] = x__compute_breadth__mutmut_124 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_125'] = x__compute_breadth__mutmut_125 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_126'] = x__compute_breadth__mutmut_126 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_127'] = x__compute_breadth__mutmut_127 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_128'] = x__compute_breadth__mutmut_128 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_129'] = x__compute_breadth__mutmut_129 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_130'] = x__compute_breadth__mutmut_130 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_131'] = x__compute_breadth__mutmut_131 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_132'] = x__compute_breadth__mutmut_132 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_133'] = x__compute_breadth__mutmut_133 # type: ignore # mutmut generated
mutants_x__compute_breadth__mutmut['x__compute_breadth__mutmut_134'] = x__compute_breadth__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_market_breadth__mutmut)
async def get_market_breadth() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_orig() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_1() -> dict | None:
    now = None
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_2() -> dict | None:
    now = time.time()
    if _cache["data"] or now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_3() -> dict | None:
    now = time.time()
    if _cache["XXdataXX"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_4() -> dict | None:
    now = time.time()
    if _cache["DATA"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_5() -> dict | None:
    now = time.time()
    if _cache["data"] and now + _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_6() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["XXtsXX"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_7() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["TS"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_8() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] <= CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_9() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["XXdataXX"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_10() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["DATA"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_11() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = None
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_12() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, None)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_13() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(_compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_14() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, )
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_15() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = None
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_16() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["XXdataXX"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_17() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["DATA"] = result
        _cache["ts"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_18() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = None
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_19() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["XXtsXX"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_20() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["TS"] = now
    return result or _cache.get("data")


async def x_get_market_breadth__mutmut_21() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result and _cache.get("data")


async def x_get_market_breadth__mutmut_22() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get(None)


async def x_get_market_breadth__mutmut_23() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("XXdataXX")


async def x_get_market_breadth__mutmut_24() -> dict | None:
    now = time.time()
    if _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]
    result = await asyncio.get_running_loop().run_in_executor(None, _compute_breadth)
    if result:
        _cache["data"] = result
        _cache["ts"] = now
    return result or _cache.get("DATA")

mutants_x_get_market_breadth__mutmut['_mutmut_orig'] = x_get_market_breadth__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_1'] = x_get_market_breadth__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_2'] = x_get_market_breadth__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_3'] = x_get_market_breadth__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_4'] = x_get_market_breadth__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_5'] = x_get_market_breadth__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_6'] = x_get_market_breadth__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_7'] = x_get_market_breadth__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_8'] = x_get_market_breadth__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_9'] = x_get_market_breadth__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_10'] = x_get_market_breadth__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_11'] = x_get_market_breadth__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_12'] = x_get_market_breadth__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_13'] = x_get_market_breadth__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_14'] = x_get_market_breadth__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_15'] = x_get_market_breadth__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_16'] = x_get_market_breadth__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_17'] = x_get_market_breadth__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_18'] = x_get_market_breadth__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_19'] = x_get_market_breadth__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_20'] = x_get_market_breadth__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_21'] = x_get_market_breadth__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_22'] = x_get_market_breadth__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_23'] = x_get_market_breadth__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_market_breadth__mutmut['x_get_market_breadth__mutmut_24'] = x_get_market_breadth__mutmut_24 # type: ignore # mutmut generated
