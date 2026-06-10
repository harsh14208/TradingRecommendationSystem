"""
Intraday stop/target monitor.

Runs every 30 minutes during market hours (Mon–Fri 09:30–16:15 ET).
Checks every active sent BUY/SELL signal against the latest price:
  - If price breaches the stop  → mark hit_stop, exit_type='stop',  notify via Telegram
  - If price breaches the target → mark hit_target, exit_type='target', notify via Telegram

Deactivates the signal after either event so users aren't notified twice.
"""

import asyncio
import logging
import math

import yfinance as yf
from sqlalchemy import select

log = logging.getLogger("signal.trade.stop_monitor")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_current_prices__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_current_prices__mutmut)
def _fetch_current_prices(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_orig(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_1(tickers: list[str]) -> dict[str, float]:
    if tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_2(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter(None)
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_3(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("XXignoreXX")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_4(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("IGNORE")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_5(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = None
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_6(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(None, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_7(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period=None, progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_8(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=None, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_9(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=None)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_10(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_11(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_12(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_13(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, )
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_14(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="XX1dXX", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_15(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1D", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_16(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=True, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_17(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=False)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_18(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = None
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_19(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "XXCloseXX" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_20(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_21(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "CLOSE" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_22(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_23(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = None
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_24(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["XXCloseXX"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_25(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_26(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["CLOSE"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_27(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = None
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_28(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[+1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_29(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-2]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_30(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(None, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_31(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, None):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_32(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr("items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_33(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, ):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_34(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "XXitemsXX"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_35(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "ITEMS"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_36(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p or not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_37(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_38(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(None):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_39(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(None)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_40(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = None
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_41(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(None)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_42(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(None)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_43(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers or not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_44(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_45(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(None):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_46(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(None)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_47(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = None
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_48(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[1]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_49(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(None)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


def x__fetch_current_prices__mutmut_50(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(None)
        return {}

mutants_x__fetch_current_prices__mutmut['_mutmut_orig'] = x__fetch_current_prices__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_1'] = x__fetch_current_prices__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_2'] = x__fetch_current_prices__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_3'] = x__fetch_current_prices__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_4'] = x__fetch_current_prices__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_5'] = x__fetch_current_prices__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_6'] = x__fetch_current_prices__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_7'] = x__fetch_current_prices__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_8'] = x__fetch_current_prices__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_9'] = x__fetch_current_prices__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_10'] = x__fetch_current_prices__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_11'] = x__fetch_current_prices__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_12'] = x__fetch_current_prices__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_13'] = x__fetch_current_prices__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_14'] = x__fetch_current_prices__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_15'] = x__fetch_current_prices__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_16'] = x__fetch_current_prices__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_17'] = x__fetch_current_prices__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_18'] = x__fetch_current_prices__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_19'] = x__fetch_current_prices__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_20'] = x__fetch_current_prices__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_21'] = x__fetch_current_prices__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_22'] = x__fetch_current_prices__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_23'] = x__fetch_current_prices__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_24'] = x__fetch_current_prices__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_25'] = x__fetch_current_prices__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_26'] = x__fetch_current_prices__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_27'] = x__fetch_current_prices__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_28'] = x__fetch_current_prices__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_29'] = x__fetch_current_prices__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_30'] = x__fetch_current_prices__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_31'] = x__fetch_current_prices__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_32'] = x__fetch_current_prices__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_33'] = x__fetch_current_prices__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_34'] = x__fetch_current_prices__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_35'] = x__fetch_current_prices__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_36'] = x__fetch_current_prices__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_37'] = x__fetch_current_prices__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_38'] = x__fetch_current_prices__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_39'] = x__fetch_current_prices__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_40'] = x__fetch_current_prices__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_41'] = x__fetch_current_prices__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_42'] = x__fetch_current_prices__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_43'] = x__fetch_current_prices__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_44'] = x__fetch_current_prices__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_45'] = x__fetch_current_prices__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_46'] = x__fetch_current_prices__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_47'] = x__fetch_current_prices__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_48'] = x__fetch_current_prices__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_49'] = x__fetch_current_prices__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_current_prices__mutmut['x__fetch_current_prices__mutmut_50'] = x__fetch_current_prices__mutmut_50 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__send_stop_target_notification__mutmut)
async def _send_stop_target_notification(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_orig(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_1(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = None
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_2(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = None
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_3(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "XX✅XX" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_4(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event != "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_5(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "XXtargetXX" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_6(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "TARGET" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_7(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "XX⛔XX"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_8(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = None
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_9(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "XXTARGET HITXX" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_10(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "target hit" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_11(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event != "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_12(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "XXtargetXX" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_13(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "TARGET" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_14(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "XXSTOP HITXX"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_15(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "stop hit"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_16(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = None
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_17(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "XX+XX" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_18(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct > 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_19(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 1 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_20(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else "XXXX"
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_21(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = None
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_22(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(None, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_23(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, None)
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_24(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get("")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_25(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, )
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_26(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "XXXX")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_27(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = None
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_28(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company or company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_29(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company == ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_30(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else "XXXX"
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_31(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = None
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_32(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'XXaboveXX' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_33(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'ABOVE' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_34(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event != 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_35(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'XXtargetXX' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_36(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'TARGET' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_37(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'XXbelowXX'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_38(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'BELOW'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_39(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'XXtargetXX' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_40(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'TARGET' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_41(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event != 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_42(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'XXtargetXX' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_43(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'TARGET' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_44(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'XXstopXX'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_45(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'STOP'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_46(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(None, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_47(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, None, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_48(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode=None)
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_49(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_50(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_51(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, )
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_52(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="XXHTMLXX")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_53(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="html")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def x__send_stop_target_notification__mutmut_54(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(None)

mutants_x__send_stop_target_notification__mutmut['_mutmut_orig'] = x__send_stop_target_notification__mutmut_orig # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_1'] = x__send_stop_target_notification__mutmut_1 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_2'] = x__send_stop_target_notification__mutmut_2 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_3'] = x__send_stop_target_notification__mutmut_3 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_4'] = x__send_stop_target_notification__mutmut_4 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_5'] = x__send_stop_target_notification__mutmut_5 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_6'] = x__send_stop_target_notification__mutmut_6 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_7'] = x__send_stop_target_notification__mutmut_7 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_8'] = x__send_stop_target_notification__mutmut_8 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_9'] = x__send_stop_target_notification__mutmut_9 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_10'] = x__send_stop_target_notification__mutmut_10 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_11'] = x__send_stop_target_notification__mutmut_11 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_12'] = x__send_stop_target_notification__mutmut_12 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_13'] = x__send_stop_target_notification__mutmut_13 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_14'] = x__send_stop_target_notification__mutmut_14 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_15'] = x__send_stop_target_notification__mutmut_15 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_16'] = x__send_stop_target_notification__mutmut_16 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_17'] = x__send_stop_target_notification__mutmut_17 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_18'] = x__send_stop_target_notification__mutmut_18 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_19'] = x__send_stop_target_notification__mutmut_19 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_20'] = x__send_stop_target_notification__mutmut_20 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_21'] = x__send_stop_target_notification__mutmut_21 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_22'] = x__send_stop_target_notification__mutmut_22 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_23'] = x__send_stop_target_notification__mutmut_23 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_24'] = x__send_stop_target_notification__mutmut_24 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_25'] = x__send_stop_target_notification__mutmut_25 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_26'] = x__send_stop_target_notification__mutmut_26 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_27'] = x__send_stop_target_notification__mutmut_27 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_28'] = x__send_stop_target_notification__mutmut_28 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_29'] = x__send_stop_target_notification__mutmut_29 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_30'] = x__send_stop_target_notification__mutmut_30 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_31'] = x__send_stop_target_notification__mutmut_31 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_32'] = x__send_stop_target_notification__mutmut_32 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_33'] = x__send_stop_target_notification__mutmut_33 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_34'] = x__send_stop_target_notification__mutmut_34 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_35'] = x__send_stop_target_notification__mutmut_35 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_36'] = x__send_stop_target_notification__mutmut_36 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_37'] = x__send_stop_target_notification__mutmut_37 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_38'] = x__send_stop_target_notification__mutmut_38 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_39'] = x__send_stop_target_notification__mutmut_39 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_40'] = x__send_stop_target_notification__mutmut_40 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_41'] = x__send_stop_target_notification__mutmut_41 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_42'] = x__send_stop_target_notification__mutmut_42 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_43'] = x__send_stop_target_notification__mutmut_43 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_44'] = x__send_stop_target_notification__mutmut_44 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_45'] = x__send_stop_target_notification__mutmut_45 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_46'] = x__send_stop_target_notification__mutmut_46 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_47'] = x__send_stop_target_notification__mutmut_47 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_48'] = x__send_stop_target_notification__mutmut_48 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_49'] = x__send_stop_target_notification__mutmut_49 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_50'] = x__send_stop_target_notification__mutmut_50 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_51'] = x__send_stop_target_notification__mutmut_51 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_52'] = x__send_stop_target_notification__mutmut_52 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_53'] = x__send_stop_target_notification__mutmut_53 # type: ignore # mutmut generated
mutants_x__send_stop_target_notification__mutmut['x__send_stop_target_notification__mutmut_54'] = x__send_stop_target_notification__mutmut_54 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_check_stop_targets_and_notify__mutmut)
async def check_stop_targets_and_notify():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_orig():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_1():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info(None)

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_2():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("XX[stop_monitor] checking active signals for stop/target hits…XX")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_3():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[STOP_MONITOR] CHECKING ACTIVE SIGNALS FOR STOP/TARGET HITS…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_4():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = None

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_5():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    None
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_6():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        None,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_7():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        None,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_8():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        None,
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_9():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        None,
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_10():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        None,
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_11():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        None,
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_12():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        None,  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_13():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_14():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_15():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_16():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_17():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_18():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_19():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_20():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(None).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_21():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent != True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_22():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == False,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_23():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active != True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_24():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == False,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_25():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(None),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_26():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["XXBUYXX", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_27():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["buy", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_28():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "XXSELLXX"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_29():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "sell"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_30():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_31():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info(None)
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_32():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("XX[stop_monitor] no active signals to check.XX")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_33():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[STOP_MONITOR] NO ACTIVE SIGNALS TO CHECK.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_34():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = None
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_35():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list(None)
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_36():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = None
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_37():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(None)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_38():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(None)

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_39():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = None

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_40():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 1

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_41():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = None
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_42():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(None)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_43():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_44():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                break

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_45():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = None
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_46():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = None
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_47():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = None
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_48():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = None

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_49():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action != "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_50():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "XXBUYXX"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_51():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "buy"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_52():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = None
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_53():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current < stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_54():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current > stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_55():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = None

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_56():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current > target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_57():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current < target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_58():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop or not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_59():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_60():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_61():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                break

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_62():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = None
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_63():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "XXtargetXX" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_64():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "TARGET" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_65():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "XXstopXX"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_66():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "STOP"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_67():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = None

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_68():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry or entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_69():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry >= 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_70():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 1:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_71():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = None
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_72():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry / 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_73():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) * entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_74():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level + entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_75():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 101
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_76():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = None
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_77():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(None, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_78():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, None)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_79():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_80():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, )
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_81():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else +raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_82():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 3)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_83():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = None

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_84():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 1.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_85():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = None
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_86():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(None)).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_87():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(None))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_88():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(None).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_89():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id != sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_90():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_91():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                break

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_92():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = None
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_93():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = None
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_94():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = None
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_95():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = None  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_96():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = True  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_97():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = None  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_98():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated = 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_99():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated -= 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_100():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 2

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_101():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                None
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_102():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(None, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_103():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, None, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_104():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, None, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_105():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, None, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_106():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, None, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_107():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, None, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_108():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, None)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_109():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_110():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_111():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_112():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_113():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_114():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_115():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, )
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_116():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                None
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_117():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.lower()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")


async def x_check_stop_targets_and_notify__mutmut_118():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(None)

mutants_x_check_stop_targets_and_notify__mutmut['_mutmut_orig'] = x_check_stop_targets_and_notify__mutmut_orig # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_1'] = x_check_stop_targets_and_notify__mutmut_1 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_2'] = x_check_stop_targets_and_notify__mutmut_2 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_3'] = x_check_stop_targets_and_notify__mutmut_3 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_4'] = x_check_stop_targets_and_notify__mutmut_4 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_5'] = x_check_stop_targets_and_notify__mutmut_5 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_6'] = x_check_stop_targets_and_notify__mutmut_6 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_7'] = x_check_stop_targets_and_notify__mutmut_7 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_8'] = x_check_stop_targets_and_notify__mutmut_8 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_9'] = x_check_stop_targets_and_notify__mutmut_9 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_10'] = x_check_stop_targets_and_notify__mutmut_10 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_11'] = x_check_stop_targets_and_notify__mutmut_11 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_12'] = x_check_stop_targets_and_notify__mutmut_12 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_13'] = x_check_stop_targets_and_notify__mutmut_13 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_14'] = x_check_stop_targets_and_notify__mutmut_14 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_15'] = x_check_stop_targets_and_notify__mutmut_15 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_16'] = x_check_stop_targets_and_notify__mutmut_16 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_17'] = x_check_stop_targets_and_notify__mutmut_17 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_18'] = x_check_stop_targets_and_notify__mutmut_18 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_19'] = x_check_stop_targets_and_notify__mutmut_19 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_20'] = x_check_stop_targets_and_notify__mutmut_20 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_21'] = x_check_stop_targets_and_notify__mutmut_21 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_22'] = x_check_stop_targets_and_notify__mutmut_22 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_23'] = x_check_stop_targets_and_notify__mutmut_23 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_24'] = x_check_stop_targets_and_notify__mutmut_24 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_25'] = x_check_stop_targets_and_notify__mutmut_25 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_26'] = x_check_stop_targets_and_notify__mutmut_26 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_27'] = x_check_stop_targets_and_notify__mutmut_27 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_28'] = x_check_stop_targets_and_notify__mutmut_28 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_29'] = x_check_stop_targets_and_notify__mutmut_29 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_30'] = x_check_stop_targets_and_notify__mutmut_30 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_31'] = x_check_stop_targets_and_notify__mutmut_31 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_32'] = x_check_stop_targets_and_notify__mutmut_32 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_33'] = x_check_stop_targets_and_notify__mutmut_33 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_34'] = x_check_stop_targets_and_notify__mutmut_34 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_35'] = x_check_stop_targets_and_notify__mutmut_35 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_36'] = x_check_stop_targets_and_notify__mutmut_36 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_37'] = x_check_stop_targets_and_notify__mutmut_37 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_38'] = x_check_stop_targets_and_notify__mutmut_38 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_39'] = x_check_stop_targets_and_notify__mutmut_39 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_40'] = x_check_stop_targets_and_notify__mutmut_40 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_41'] = x_check_stop_targets_and_notify__mutmut_41 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_42'] = x_check_stop_targets_and_notify__mutmut_42 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_43'] = x_check_stop_targets_and_notify__mutmut_43 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_44'] = x_check_stop_targets_and_notify__mutmut_44 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_45'] = x_check_stop_targets_and_notify__mutmut_45 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_46'] = x_check_stop_targets_and_notify__mutmut_46 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_47'] = x_check_stop_targets_and_notify__mutmut_47 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_48'] = x_check_stop_targets_and_notify__mutmut_48 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_49'] = x_check_stop_targets_and_notify__mutmut_49 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_50'] = x_check_stop_targets_and_notify__mutmut_50 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_51'] = x_check_stop_targets_and_notify__mutmut_51 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_52'] = x_check_stop_targets_and_notify__mutmut_52 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_53'] = x_check_stop_targets_and_notify__mutmut_53 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_54'] = x_check_stop_targets_and_notify__mutmut_54 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_55'] = x_check_stop_targets_and_notify__mutmut_55 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_56'] = x_check_stop_targets_and_notify__mutmut_56 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_57'] = x_check_stop_targets_and_notify__mutmut_57 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_58'] = x_check_stop_targets_and_notify__mutmut_58 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_59'] = x_check_stop_targets_and_notify__mutmut_59 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_60'] = x_check_stop_targets_and_notify__mutmut_60 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_61'] = x_check_stop_targets_and_notify__mutmut_61 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_62'] = x_check_stop_targets_and_notify__mutmut_62 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_63'] = x_check_stop_targets_and_notify__mutmut_63 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_64'] = x_check_stop_targets_and_notify__mutmut_64 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_65'] = x_check_stop_targets_and_notify__mutmut_65 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_66'] = x_check_stop_targets_and_notify__mutmut_66 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_67'] = x_check_stop_targets_and_notify__mutmut_67 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_68'] = x_check_stop_targets_and_notify__mutmut_68 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_69'] = x_check_stop_targets_and_notify__mutmut_69 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_70'] = x_check_stop_targets_and_notify__mutmut_70 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_71'] = x_check_stop_targets_and_notify__mutmut_71 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_72'] = x_check_stop_targets_and_notify__mutmut_72 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_73'] = x_check_stop_targets_and_notify__mutmut_73 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_74'] = x_check_stop_targets_and_notify__mutmut_74 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_75'] = x_check_stop_targets_and_notify__mutmut_75 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_76'] = x_check_stop_targets_and_notify__mutmut_76 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_77'] = x_check_stop_targets_and_notify__mutmut_77 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_78'] = x_check_stop_targets_and_notify__mutmut_78 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_79'] = x_check_stop_targets_and_notify__mutmut_79 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_80'] = x_check_stop_targets_and_notify__mutmut_80 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_81'] = x_check_stop_targets_and_notify__mutmut_81 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_82'] = x_check_stop_targets_and_notify__mutmut_82 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_83'] = x_check_stop_targets_and_notify__mutmut_83 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_84'] = x_check_stop_targets_and_notify__mutmut_84 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_85'] = x_check_stop_targets_and_notify__mutmut_85 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_86'] = x_check_stop_targets_and_notify__mutmut_86 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_87'] = x_check_stop_targets_and_notify__mutmut_87 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_88'] = x_check_stop_targets_and_notify__mutmut_88 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_89'] = x_check_stop_targets_and_notify__mutmut_89 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_90'] = x_check_stop_targets_and_notify__mutmut_90 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_91'] = x_check_stop_targets_and_notify__mutmut_91 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_92'] = x_check_stop_targets_and_notify__mutmut_92 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_93'] = x_check_stop_targets_and_notify__mutmut_93 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_94'] = x_check_stop_targets_and_notify__mutmut_94 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_95'] = x_check_stop_targets_and_notify__mutmut_95 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_96'] = x_check_stop_targets_and_notify__mutmut_96 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_97'] = x_check_stop_targets_and_notify__mutmut_97 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_98'] = x_check_stop_targets_and_notify__mutmut_98 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_99'] = x_check_stop_targets_and_notify__mutmut_99 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_100'] = x_check_stop_targets_and_notify__mutmut_100 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_101'] = x_check_stop_targets_and_notify__mutmut_101 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_102'] = x_check_stop_targets_and_notify__mutmut_102 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_103'] = x_check_stop_targets_and_notify__mutmut_103 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_104'] = x_check_stop_targets_and_notify__mutmut_104 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_105'] = x_check_stop_targets_and_notify__mutmut_105 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_106'] = x_check_stop_targets_and_notify__mutmut_106 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_107'] = x_check_stop_targets_and_notify__mutmut_107 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_108'] = x_check_stop_targets_and_notify__mutmut_108 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_109'] = x_check_stop_targets_and_notify__mutmut_109 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_110'] = x_check_stop_targets_and_notify__mutmut_110 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_111'] = x_check_stop_targets_and_notify__mutmut_111 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_112'] = x_check_stop_targets_and_notify__mutmut_112 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_113'] = x_check_stop_targets_and_notify__mutmut_113 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_114'] = x_check_stop_targets_and_notify__mutmut_114 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_115'] = x_check_stop_targets_and_notify__mutmut_115 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_116'] = x_check_stop_targets_and_notify__mutmut_116 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_117'] = x_check_stop_targets_and_notify__mutmut_117 # type: ignore # mutmut generated
mutants_x_check_stop_targets_and_notify__mutmut['x_check_stop_targets_and_notify__mutmut_118'] = x_check_stop_targets_and_notify__mutmut_118 # type: ignore # mutmut generated
