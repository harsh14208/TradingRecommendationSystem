"""
Google Trends — rising search volume for a ticker signals retail FOMO.
Uses pytrends (free, no API key). Cached 6h per ticker.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger("signal.trade.trends")

_executor = ThreadPoolExecutor(max_workers=1)  # pytrends is not thread-safe at scale
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 21600  # 6 hours — successful results
_BACKOFF_TTL = 1800  # 30 min — cache empty on failure so we don't hammer the API


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_trends__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_trends__mutmut)
def _fetch_trends(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_orig(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_1(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = None
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_2(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl=None, tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_3(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=None, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_4(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=None)
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_5(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_6(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_7(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, )
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_8(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="XXen-USXX", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_9(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-us", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_10(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="EN-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_11(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=361, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_12(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(11, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_13(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 26))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_14(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = None
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_15(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload(None, cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_16(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=None, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_17(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe=None, geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_18(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo=None)
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_19(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload(cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_20(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_21(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_22(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", )
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_23(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=1, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_24(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="XXtoday 3-mXX", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_25(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="TODAY 3-M", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_26(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="XXUSXX")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_27(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="us")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_28(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = None
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_29(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty and kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_30(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None and df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_31(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is not None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_32(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_33(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = None
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_34(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) <= 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_35(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 9:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_36(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = None  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_37(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(None)  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_38(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[+1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_39(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-2])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_40(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = None  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_41(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(None)  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_42(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[+5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_43(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-6:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_44(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:+1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_45(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-2].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_46(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = None
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_47(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(None)
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_48(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior < 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_49(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 1:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_50(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = None
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_51(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round(None, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_52(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, None)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_53(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round(1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_54(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, )
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_55(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior / 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_56(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) * prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_57(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent + prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_58(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 101, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_59(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 2)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_60(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = None
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_61(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round(None, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_62(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, None)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_63(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round(1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_64(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, )
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_65(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) / 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_66(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) * max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_67(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent + avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_68(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(None, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_69(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, None) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_70(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_71(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, ) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_72(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 2) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_73(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 101, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_74(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 2)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_75(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 or recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_76(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct >= 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_77(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 101 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_78(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent >= avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_79(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m / 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_80(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 2.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_81(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = None
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_82(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "XXbullishXX", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_83(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "BULLISH", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_84(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 7
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_85(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct >= 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_86(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 51:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_87(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = None
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_88(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "XXbullishXX", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_89(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "BULLISH", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_90(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 4
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_91(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 or recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_92(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct <= -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_93(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < +50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_94(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -51 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_95(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent <= avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_96(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m / 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_97(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 1.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_98(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = None
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_99(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "XXbearishXX", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_100(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "BEARISH", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_101(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", +3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_102(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -4
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_103(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = None
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_104(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "XXneutralXX", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_105(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "NEUTRAL", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_106(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 1
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_107(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "XXrecentXX": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_108(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "RECENT": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_109(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "XXprior_4wXX": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_110(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "PRIOR_4W": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_111(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(None, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_112(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, None),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_113(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_114(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, ),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_115(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 2),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_116(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "XXavg_3mXX": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_117(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "AVG_3M": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_118(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(None, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_119(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, None),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_120(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_121(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, ),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_122(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 2),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_123(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "XXchange_pctXX": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_124(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "CHANGE_PCT": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_125(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "XXvs_avg_pctXX": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_126(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "VS_AVG_PCT": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_127(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "XXsignalXX": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_128(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "SIGNAL": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_129(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "XXscoreXX": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_130(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "SCORE": score,
        }
    except Exception as e:
        log.warning(f"[trends] {ticker}: {e}")
        return {}


def x__fetch_trends__mutmut_131(ticker: str) -> dict:
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw = f"{ticker} stock"
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="US")
        df = pt.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {}
        series = df[kw].dropna()
        if len(series) < 8:
            return {}
        recent = float(series.iloc[-1])  # last week
        prior = float(series.iloc[-5:-1].mean())  # prior 4 weeks avg
        avg_3m = float(series.mean())
        if prior <= 0:
            return {}
        change_pct = round((recent - prior) / prior * 100, 1)
        vs_avg = round((recent - avg_3m) / max(avg_3m, 1) * 100, 1)
        if change_pct > 100 and recent > avg_3m * 1.5:
            signal, score = "bullish", 6
        elif change_pct > 50:
            signal, score = "bullish", 3
        elif change_pct < -50 and recent < avg_3m * 0.5:
            signal, score = "bearish", -3
        else:
            signal, score = "neutral", 0
        return {
            "recent": recent,
            "prior_4w": round(prior, 1),
            "avg_3m": round(avg_3m, 1),
            "change_pct": change_pct,
            "vs_avg_pct": vs_avg,
            "signal": signal,
            "score": score,
        }
    except Exception as e:
        log.warning(None)
        return {}

mutants_x__fetch_trends__mutmut['_mutmut_orig'] = x__fetch_trends__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_1'] = x__fetch_trends__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_2'] = x__fetch_trends__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_3'] = x__fetch_trends__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_4'] = x__fetch_trends__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_5'] = x__fetch_trends__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_6'] = x__fetch_trends__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_7'] = x__fetch_trends__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_8'] = x__fetch_trends__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_9'] = x__fetch_trends__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_10'] = x__fetch_trends__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_11'] = x__fetch_trends__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_12'] = x__fetch_trends__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_13'] = x__fetch_trends__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_14'] = x__fetch_trends__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_15'] = x__fetch_trends__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_16'] = x__fetch_trends__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_17'] = x__fetch_trends__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_18'] = x__fetch_trends__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_19'] = x__fetch_trends__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_20'] = x__fetch_trends__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_21'] = x__fetch_trends__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_22'] = x__fetch_trends__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_23'] = x__fetch_trends__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_24'] = x__fetch_trends__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_25'] = x__fetch_trends__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_26'] = x__fetch_trends__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_27'] = x__fetch_trends__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_28'] = x__fetch_trends__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_29'] = x__fetch_trends__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_30'] = x__fetch_trends__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_31'] = x__fetch_trends__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_32'] = x__fetch_trends__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_33'] = x__fetch_trends__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_34'] = x__fetch_trends__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_35'] = x__fetch_trends__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_36'] = x__fetch_trends__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_37'] = x__fetch_trends__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_38'] = x__fetch_trends__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_39'] = x__fetch_trends__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_40'] = x__fetch_trends__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_41'] = x__fetch_trends__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_42'] = x__fetch_trends__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_43'] = x__fetch_trends__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_44'] = x__fetch_trends__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_45'] = x__fetch_trends__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_46'] = x__fetch_trends__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_47'] = x__fetch_trends__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_48'] = x__fetch_trends__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_49'] = x__fetch_trends__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_50'] = x__fetch_trends__mutmut_50 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_51'] = x__fetch_trends__mutmut_51 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_52'] = x__fetch_trends__mutmut_52 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_53'] = x__fetch_trends__mutmut_53 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_54'] = x__fetch_trends__mutmut_54 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_55'] = x__fetch_trends__mutmut_55 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_56'] = x__fetch_trends__mutmut_56 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_57'] = x__fetch_trends__mutmut_57 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_58'] = x__fetch_trends__mutmut_58 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_59'] = x__fetch_trends__mutmut_59 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_60'] = x__fetch_trends__mutmut_60 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_61'] = x__fetch_trends__mutmut_61 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_62'] = x__fetch_trends__mutmut_62 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_63'] = x__fetch_trends__mutmut_63 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_64'] = x__fetch_trends__mutmut_64 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_65'] = x__fetch_trends__mutmut_65 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_66'] = x__fetch_trends__mutmut_66 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_67'] = x__fetch_trends__mutmut_67 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_68'] = x__fetch_trends__mutmut_68 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_69'] = x__fetch_trends__mutmut_69 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_70'] = x__fetch_trends__mutmut_70 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_71'] = x__fetch_trends__mutmut_71 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_72'] = x__fetch_trends__mutmut_72 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_73'] = x__fetch_trends__mutmut_73 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_74'] = x__fetch_trends__mutmut_74 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_75'] = x__fetch_trends__mutmut_75 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_76'] = x__fetch_trends__mutmut_76 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_77'] = x__fetch_trends__mutmut_77 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_78'] = x__fetch_trends__mutmut_78 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_79'] = x__fetch_trends__mutmut_79 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_80'] = x__fetch_trends__mutmut_80 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_81'] = x__fetch_trends__mutmut_81 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_82'] = x__fetch_trends__mutmut_82 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_83'] = x__fetch_trends__mutmut_83 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_84'] = x__fetch_trends__mutmut_84 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_85'] = x__fetch_trends__mutmut_85 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_86'] = x__fetch_trends__mutmut_86 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_87'] = x__fetch_trends__mutmut_87 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_88'] = x__fetch_trends__mutmut_88 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_89'] = x__fetch_trends__mutmut_89 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_90'] = x__fetch_trends__mutmut_90 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_91'] = x__fetch_trends__mutmut_91 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_92'] = x__fetch_trends__mutmut_92 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_93'] = x__fetch_trends__mutmut_93 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_94'] = x__fetch_trends__mutmut_94 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_95'] = x__fetch_trends__mutmut_95 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_96'] = x__fetch_trends__mutmut_96 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_97'] = x__fetch_trends__mutmut_97 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_98'] = x__fetch_trends__mutmut_98 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_99'] = x__fetch_trends__mutmut_99 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_100'] = x__fetch_trends__mutmut_100 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_101'] = x__fetch_trends__mutmut_101 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_102'] = x__fetch_trends__mutmut_102 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_103'] = x__fetch_trends__mutmut_103 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_104'] = x__fetch_trends__mutmut_104 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_105'] = x__fetch_trends__mutmut_105 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_106'] = x__fetch_trends__mutmut_106 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_107'] = x__fetch_trends__mutmut_107 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_108'] = x__fetch_trends__mutmut_108 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_109'] = x__fetch_trends__mutmut_109 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_110'] = x__fetch_trends__mutmut_110 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_111'] = x__fetch_trends__mutmut_111 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_112'] = x__fetch_trends__mutmut_112 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_113'] = x__fetch_trends__mutmut_113 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_114'] = x__fetch_trends__mutmut_114 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_115'] = x__fetch_trends__mutmut_115 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_116'] = x__fetch_trends__mutmut_116 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_117'] = x__fetch_trends__mutmut_117 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_118'] = x__fetch_trends__mutmut_118 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_119'] = x__fetch_trends__mutmut_119 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_120'] = x__fetch_trends__mutmut_120 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_121'] = x__fetch_trends__mutmut_121 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_122'] = x__fetch_trends__mutmut_122 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_123'] = x__fetch_trends__mutmut_123 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_124'] = x__fetch_trends__mutmut_124 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_125'] = x__fetch_trends__mutmut_125 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_126'] = x__fetch_trends__mutmut_126 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_127'] = x__fetch_trends__mutmut_127 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_128'] = x__fetch_trends__mutmut_128 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_129'] = x__fetch_trends__mutmut_129 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_130'] = x__fetch_trends__mutmut_130 # type: ignore # mutmut generated
mutants_x__fetch_trends__mutmut['x__fetch_trends__mutmut_131'] = x__fetch_trends__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_google_trends__mutmut)
async def get_google_trends(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_orig(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_1(ticker: str) -> dict:
    cached = None
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_2(ticker: str) -> dict:
    cached = _cache.get(None)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_3(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached or time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_4(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() + cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_5(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[2] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_6(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] <= CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_7(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[1]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_8(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = None
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_9(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(None, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_10(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, None, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_11(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, None)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_12(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_13(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_14(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, )
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_15(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = None
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_16(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = None
    return result or {}


async def x_get_google_trends__mutmut_17(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result and {}, time.time() - (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_18(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() + (CACHE_TTL - ttl))
    return result or {}


async def x_get_google_trends__mutmut_19(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL + ttl))
    return result or {}


async def x_get_google_trends__mutmut_20(ticker: str) -> dict:
    cached = _cache.get(ticker)
    if cached and time.time() - cached[1] < CACHE_TTL:
        return cached[0]
    result = await asyncio.get_running_loop().run_in_executor(_executor, _fetch_trends, ticker)
    ttl = CACHE_TTL if result else _BACKOFF_TTL
    _cache[ticker] = (result or {}, time.time() - (CACHE_TTL - ttl))
    return result and {}

mutants_x_get_google_trends__mutmut['_mutmut_orig'] = x_get_google_trends__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_1'] = x_get_google_trends__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_2'] = x_get_google_trends__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_3'] = x_get_google_trends__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_4'] = x_get_google_trends__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_5'] = x_get_google_trends__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_6'] = x_get_google_trends__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_7'] = x_get_google_trends__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_8'] = x_get_google_trends__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_9'] = x_get_google_trends__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_10'] = x_get_google_trends__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_11'] = x_get_google_trends__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_12'] = x_get_google_trends__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_13'] = x_get_google_trends__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_14'] = x_get_google_trends__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_15'] = x_get_google_trends__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_16'] = x_get_google_trends__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_17'] = x_get_google_trends__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_18'] = x_get_google_trends__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_19'] = x_get_google_trends__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_google_trends__mutmut['x_get_google_trends__mutmut_20'] = x_get_google_trends__mutmut_20 # type: ignore # mutmut generated
