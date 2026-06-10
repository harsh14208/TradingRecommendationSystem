"""
Alternative Data: Supply Chain Signals

Data sources (all free / no extra API key required):
  1. Energy demand proxy — Brent crude 20-day momentum via yfinance
  2. Freight proxy — Cass Freight Index (via FRED if key available)

Sector impact map:
  Energy demand spike → bullish: XOM, CVX, SLB, EOG, XLE, PALL, GLD
  Freight contraction → bearish: UPS, FDX, UNP, CSX, XPO

Cached for 4 hours.

NOTE (v8.2, 2026-06-09): BDI (^BDI) fetch removed — yfinance returns 404
(delisted/unavailable). The Stooq endpoint mentioned in the original docstring
also failed. Energy and freight fetches remain active.
"""

import asyncio
import logging
import time
from services.http_client import shared_session

log = logging.getLogger("signal.trade.supply_chain")

_cache: dict = {"result": None, "ts": 0.0}
_TTL = 14400  # 4 hours

# Sector impact mapping
_ENERGY_BULL = {"XOM", "CVX", "SLB", "EOG", "XLE", "PALL", "GLD"}
_FREIGHT_BEAR = {"UPS", "FDX", "UNP", "CSX", "XPO"}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__fetch_energy_momentum__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_energy_momentum__mutmut)
async def _fetch_energy_momentum() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_orig() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_1() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = None
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_2() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history(None, period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_3() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period=None, interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_4() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval=None)
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_5() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history(period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_6() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_7() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", )
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_8() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("XXBZ=FXX", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_9() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("bz=f", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_10() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="XX3moXX", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_11() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3MO", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_12() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="XX1dXX")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_13() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1D")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_14() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty and len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_15() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None and df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_16() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is not None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_17() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) <= 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_18() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 23:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_19() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = None
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_20() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(None)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_21() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["XXCloseXX"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_22() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_23() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["CLOSE"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_24() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = None
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_25() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(None)
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_26() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[+1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_27() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-2])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_28() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = None
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_29() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(None)
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_30() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[+21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_31() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-22])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_32() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = None
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_33() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 / 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_34() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) * prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_35() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest + prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_36() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 101
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_37() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "XXbrent_priceXX": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_38() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "BRENT_PRICE": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_39() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(None, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_40() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, None),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_41() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_42() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, ),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_43() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 3),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_44() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "XXchg_20d_pctXX": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_45() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "CHG_20D_PCT": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_46() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(None, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_47() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, None),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_48() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_49() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, ),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_50() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 2),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_51() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "XXtrendXX": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_52() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "TREND": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_53() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "XXbullXX" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_54() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "BULL" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_55() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d >= 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_56() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 6 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_57() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "XXbearXX" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_58() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "BEAR" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_59() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d <= -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_60() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < +5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_61() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -6 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_62() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "XXneutralXX",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_63() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "NEUTRAL",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Brent fetch failed: {e}")
        return None


async def x__fetch_energy_momentum__mutmut_64() -> dict | None:
    """Brent crude 20-day momentum as energy demand proxy."""
    try:
        from services.market_data import get_history

        df = await get_history("BZ=F", period="3mo", interval="1d")
        if df is None or df.empty or len(df) < 22:
            return None
        closes = df["Close"].astype(float)
        latest = float(closes.iloc[-1])
        prev20 = float(closes.iloc[-21])
        chg_20d = (latest - prev20) / prev20 * 100
        return {
            "brent_price": round(latest, 2),
            "chg_20d_pct": round(chg_20d, 1),
            "trend": "bull" if chg_20d > 5 else "bear" if chg_20d < -5 else "neutral",
        }
    except Exception as e:
        log.debug(None)
        return None

mutants_x__fetch_energy_momentum__mutmut['_mutmut_orig'] = x__fetch_energy_momentum__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_1'] = x__fetch_energy_momentum__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_2'] = x__fetch_energy_momentum__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_3'] = x__fetch_energy_momentum__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_4'] = x__fetch_energy_momentum__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_5'] = x__fetch_energy_momentum__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_6'] = x__fetch_energy_momentum__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_7'] = x__fetch_energy_momentum__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_8'] = x__fetch_energy_momentum__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_9'] = x__fetch_energy_momentum__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_10'] = x__fetch_energy_momentum__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_11'] = x__fetch_energy_momentum__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_12'] = x__fetch_energy_momentum__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_13'] = x__fetch_energy_momentum__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_14'] = x__fetch_energy_momentum__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_15'] = x__fetch_energy_momentum__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_16'] = x__fetch_energy_momentum__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_17'] = x__fetch_energy_momentum__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_18'] = x__fetch_energy_momentum__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_19'] = x__fetch_energy_momentum__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_20'] = x__fetch_energy_momentum__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_21'] = x__fetch_energy_momentum__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_22'] = x__fetch_energy_momentum__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_23'] = x__fetch_energy_momentum__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_24'] = x__fetch_energy_momentum__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_25'] = x__fetch_energy_momentum__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_26'] = x__fetch_energy_momentum__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_27'] = x__fetch_energy_momentum__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_28'] = x__fetch_energy_momentum__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_29'] = x__fetch_energy_momentum__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_30'] = x__fetch_energy_momentum__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_31'] = x__fetch_energy_momentum__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_32'] = x__fetch_energy_momentum__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_33'] = x__fetch_energy_momentum__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_34'] = x__fetch_energy_momentum__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_35'] = x__fetch_energy_momentum__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_36'] = x__fetch_energy_momentum__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_37'] = x__fetch_energy_momentum__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_38'] = x__fetch_energy_momentum__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_39'] = x__fetch_energy_momentum__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_40'] = x__fetch_energy_momentum__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_41'] = x__fetch_energy_momentum__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_42'] = x__fetch_energy_momentum__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_43'] = x__fetch_energy_momentum__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_44'] = x__fetch_energy_momentum__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_45'] = x__fetch_energy_momentum__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_46'] = x__fetch_energy_momentum__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_47'] = x__fetch_energy_momentum__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_48'] = x__fetch_energy_momentum__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_49'] = x__fetch_energy_momentum__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_50'] = x__fetch_energy_momentum__mutmut_50 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_51'] = x__fetch_energy_momentum__mutmut_51 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_52'] = x__fetch_energy_momentum__mutmut_52 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_53'] = x__fetch_energy_momentum__mutmut_53 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_54'] = x__fetch_energy_momentum__mutmut_54 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_55'] = x__fetch_energy_momentum__mutmut_55 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_56'] = x__fetch_energy_momentum__mutmut_56 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_57'] = x__fetch_energy_momentum__mutmut_57 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_58'] = x__fetch_energy_momentum__mutmut_58 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_59'] = x__fetch_energy_momentum__mutmut_59 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_60'] = x__fetch_energy_momentum__mutmut_60 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_61'] = x__fetch_energy_momentum__mutmut_61 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_62'] = x__fetch_energy_momentum__mutmut_62 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_63'] = x__fetch_energy_momentum__mutmut_63 # type: ignore # mutmut generated
mutants_x__fetch_energy_momentum__mutmut['x__fetch_energy_momentum__mutmut_64'] = x__fetch_energy_momentum__mutmut_64 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__fetch_freight_fred__mutmut)
async def _fetch_freight_fred() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_orig() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_1() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = None
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_2() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_3() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = None
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_4() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(None, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_5() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=None) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_6() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_7() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_8() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=None)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_9() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=9)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_10() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_11() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 201:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_12() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = None

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_13() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = None
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_14() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get(None, []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_15() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", None) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_16() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get([]) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_17() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", ) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_18() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("XXobservationsXX", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_19() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("OBSERVATIONS", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_20() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get(None) != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_21() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("XXvalueXX") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_22() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("VALUE") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_23() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") == "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_24() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "XX.XX"]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_25() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) <= 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_26() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 4:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_27() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = None  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_28() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(None) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_29() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["XXvalueXX"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_30() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["VALUE"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_31() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:13]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_32() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = None
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_33() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[1]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_34() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = None
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_35() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[7] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_36() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) >= 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_37() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 7 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_38() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[+1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_39() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-2]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_40() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = None

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_41() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 / 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_42() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) * prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_43() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest + prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_44() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 101

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_45() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "XXcass_freightXX": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_46() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "CASS_FREIGHT": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_47() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(None, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_48() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, None),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_49() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_50() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, ),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_51() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 3),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_52() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "XXchg_6m_pctXX": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_53() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "CHG_6M_PCT": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_54() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(None, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_55() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, None),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_56() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_57() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, ),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_58() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 2),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_59() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "XXtrendXX": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_60() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "TREND": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_61() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "XXbullXX" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_62() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "BULL" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_63() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m >= 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_64() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 6 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_65() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "XXbearXX" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_66() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "BEAR" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_67() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m <= -5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_68() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < +5 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_69() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -6 else "neutral",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_70() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "XXneutralXX",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_71() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "NEUTRAL",
        }
    except Exception as e:
        log.debug(f"[supply_chain] Cass freight FRED failed: {e}")
        return None


async def x__fetch_freight_fred__mutmut_72() -> dict | None:
    """
    Cass Freight Index from FRED (requires FRED API key).
    Series: CASSFREIGHTEXPNS (expenditures) or CASSFREIGHT (shipments)
    """
    try:
        from config import get_settings

        key = get_settings().fred_api_key
        if not key:
            return None
        import aiohttp

        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=CASSFREIGHTEXPNS&sort_order=desc&limit=24"
            f"&api_key={key}&file_type=json"
        )
        async with shared_session() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        obs = [o for o in data.get("observations", []) if o.get("value") != "."]
        if len(obs) < 3:
            return None

        vals = [float(o["value"]) for o in obs[:12]]  # newest first
        latest = vals[0]
        prev6 = vals[6] if len(vals) > 6 else vals[-1]
        chg_6m = (latest - prev6) / prev6 * 100

        return {
            "cass_freight": round(latest, 2),
            "chg_6m_pct": round(chg_6m, 1),
            "trend": "bull" if chg_6m > 5 else "bear" if chg_6m < -5 else "neutral",
        }
    except Exception as e:
        log.debug(None)
        return None

mutants_x__fetch_freight_fred__mutmut['_mutmut_orig'] = x__fetch_freight_fred__mutmut_orig # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_1'] = x__fetch_freight_fred__mutmut_1 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_2'] = x__fetch_freight_fred__mutmut_2 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_3'] = x__fetch_freight_fred__mutmut_3 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_4'] = x__fetch_freight_fred__mutmut_4 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_5'] = x__fetch_freight_fred__mutmut_5 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_6'] = x__fetch_freight_fred__mutmut_6 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_7'] = x__fetch_freight_fred__mutmut_7 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_8'] = x__fetch_freight_fred__mutmut_8 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_9'] = x__fetch_freight_fred__mutmut_9 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_10'] = x__fetch_freight_fred__mutmut_10 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_11'] = x__fetch_freight_fred__mutmut_11 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_12'] = x__fetch_freight_fred__mutmut_12 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_13'] = x__fetch_freight_fred__mutmut_13 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_14'] = x__fetch_freight_fred__mutmut_14 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_15'] = x__fetch_freight_fred__mutmut_15 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_16'] = x__fetch_freight_fred__mutmut_16 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_17'] = x__fetch_freight_fred__mutmut_17 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_18'] = x__fetch_freight_fred__mutmut_18 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_19'] = x__fetch_freight_fred__mutmut_19 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_20'] = x__fetch_freight_fred__mutmut_20 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_21'] = x__fetch_freight_fred__mutmut_21 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_22'] = x__fetch_freight_fred__mutmut_22 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_23'] = x__fetch_freight_fred__mutmut_23 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_24'] = x__fetch_freight_fred__mutmut_24 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_25'] = x__fetch_freight_fred__mutmut_25 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_26'] = x__fetch_freight_fred__mutmut_26 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_27'] = x__fetch_freight_fred__mutmut_27 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_28'] = x__fetch_freight_fred__mutmut_28 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_29'] = x__fetch_freight_fred__mutmut_29 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_30'] = x__fetch_freight_fred__mutmut_30 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_31'] = x__fetch_freight_fred__mutmut_31 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_32'] = x__fetch_freight_fred__mutmut_32 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_33'] = x__fetch_freight_fred__mutmut_33 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_34'] = x__fetch_freight_fred__mutmut_34 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_35'] = x__fetch_freight_fred__mutmut_35 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_36'] = x__fetch_freight_fred__mutmut_36 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_37'] = x__fetch_freight_fred__mutmut_37 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_38'] = x__fetch_freight_fred__mutmut_38 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_39'] = x__fetch_freight_fred__mutmut_39 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_40'] = x__fetch_freight_fred__mutmut_40 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_41'] = x__fetch_freight_fred__mutmut_41 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_42'] = x__fetch_freight_fred__mutmut_42 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_43'] = x__fetch_freight_fred__mutmut_43 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_44'] = x__fetch_freight_fred__mutmut_44 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_45'] = x__fetch_freight_fred__mutmut_45 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_46'] = x__fetch_freight_fred__mutmut_46 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_47'] = x__fetch_freight_fred__mutmut_47 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_48'] = x__fetch_freight_fred__mutmut_48 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_49'] = x__fetch_freight_fred__mutmut_49 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_50'] = x__fetch_freight_fred__mutmut_50 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_51'] = x__fetch_freight_fred__mutmut_51 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_52'] = x__fetch_freight_fred__mutmut_52 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_53'] = x__fetch_freight_fred__mutmut_53 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_54'] = x__fetch_freight_fred__mutmut_54 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_55'] = x__fetch_freight_fred__mutmut_55 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_56'] = x__fetch_freight_fred__mutmut_56 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_57'] = x__fetch_freight_fred__mutmut_57 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_58'] = x__fetch_freight_fred__mutmut_58 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_59'] = x__fetch_freight_fred__mutmut_59 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_60'] = x__fetch_freight_fred__mutmut_60 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_61'] = x__fetch_freight_fred__mutmut_61 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_62'] = x__fetch_freight_fred__mutmut_62 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_63'] = x__fetch_freight_fred__mutmut_63 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_64'] = x__fetch_freight_fred__mutmut_64 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_65'] = x__fetch_freight_fred__mutmut_65 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_66'] = x__fetch_freight_fred__mutmut_66 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_67'] = x__fetch_freight_fred__mutmut_67 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_68'] = x__fetch_freight_fred__mutmut_68 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_69'] = x__fetch_freight_fred__mutmut_69 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_70'] = x__fetch_freight_fred__mutmut_70 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_71'] = x__fetch_freight_fred__mutmut_71 # type: ignore # mutmut generated
mutants_x__fetch_freight_fred__mutmut['x__fetch_freight_fred__mutmut_72'] = x__fetch_freight_fred__mutmut_72 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__build_sector_signals__mutmut)
def _build_sector_signals(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_orig(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_1(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = None

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_2(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_3(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = None
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_4(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"XXtickerXX": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_5(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"TICKER": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_6(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "XXscoreXX": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_7(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "SCORE": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_8(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 1.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_9(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "XXreasonsXX": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_10(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "REASONS": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_11(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] = pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_12(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] -= pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_13(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["XXscoreXX"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_14(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["SCORE"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_15(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(None)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_16(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["XXreasonsXX"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_17(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["REASONS"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_18(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = None
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_19(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["XXtrendXX"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_20(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["TREND"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_21(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = None
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_22(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["XXchg_20d_pctXX"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_23(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["CHG_20D_PCT"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_24(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend != "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_25(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "XXbullXX":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_26(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "BULL":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_27(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = None
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_28(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(None, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_29(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, None)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_30(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_31(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, )
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_32(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(7.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_33(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) / 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_34(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(None) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_35(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 1.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_36(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(None, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_37(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, None, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_38(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, None)
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_39(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(+pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_40(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_41(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, )
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_42(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_43(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend != "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_44(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "XXbearXX":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_45(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "BEAR":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_46(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = None
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_47(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(None, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_48(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, None)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_49(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_50(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, )
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_51(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(7.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_52(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) / 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_53(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(None) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_54(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 1.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_55(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(None, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_56(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, None, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_57(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, None)

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_58(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(-pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_59(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_60(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, )

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_61(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_62(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = None
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_63(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["XXtrendXX"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_64(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["TREND"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_65(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = None
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_66(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["XXchg_6m_pctXX"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_67(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["CHG_6M_PCT"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_68(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend != "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_69(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "XXbearXX":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_70(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "BEAR":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_71(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = None
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_72(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(None, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_73(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, None)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_74(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_75(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, )
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_76(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(6.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_77(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) / 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_78(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(None) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_79(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 1.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_80(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(None, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_81(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, None, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_82(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, None)
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_83(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(-pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_84(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_85(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, )
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_86(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_87(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend != "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_88(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "XXbullXX":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_89(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "BULL":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_90(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = None
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_91(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(None, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_92(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, None)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_93(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_94(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, )
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_95(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(6.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_96(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) / 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_97(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(None) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_98(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 1.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_99(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(None, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_100(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, None, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_101(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, None)

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_102(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(+pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_103(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_104(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, )

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_105(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_106(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = None
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_107(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = None
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_108(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "XXbullishXX" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_109(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "BULLISH" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_110(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["XXscoreXX"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_111(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["SCORE"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_112(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] >= 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_113(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 1 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_114(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "XXbearishXX" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_115(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "BEARISH" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_116(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["XXscoreXX"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_117(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["SCORE"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_118(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] <= 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_119(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 1 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_120(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "XXneutralXX"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_121(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "NEUTRAL"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_122(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            None
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_123(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "XXtickerXX": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_124(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "TICKER": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_125(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "XXscoreXX": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_126(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "SCORE": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_127(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(None, 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_128(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], None),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_129(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_130(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], ),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_131(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["XXscoreXX"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_132(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["SCORE"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_133(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 2),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_134(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "XXdirectionXX": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_135(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "DIRECTION": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_136(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "XXreasonsXX": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_137(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "REASONS": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_138(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["XXreasonsXX"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_139(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["REASONS"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_140(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=None, reverse=True)
    return result


def x__build_sector_signals__mutmut_141(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=None)
    return result


def x__build_sector_signals__mutmut_142(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(reverse=True)
    return result


def x__build_sector_signals__mutmut_143(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), )
    return result


def x__build_sector_signals__mutmut_144(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: None, reverse=True)
    return result


def x__build_sector_signals__mutmut_145(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(None), reverse=True)
    return result


def x__build_sector_signals__mutmut_146(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["XXscoreXX"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_147(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["SCORE"]), reverse=True)
    return result


def x__build_sector_signals__mutmut_148(energy: dict | None, freight: dict | None) -> list[dict]:
    """
    Synthesise energy + freight into per-ticker supply-chain signals.
    Returns list of {ticker, direction, score, reason}.
    """
    signals: dict[str, dict] = {}

    def add(ticker: str, pts: float, reason: str):
        if ticker not in signals:
            signals[ticker] = {"ticker": ticker, "score": 0.0, "reasons": []}
        signals[ticker]["score"] += pts
        signals[ticker]["reasons"].append(reason)

    # ── Energy demand signals ─────────────────────────────────────────────────
    if energy:
        trend = energy["trend"]
        chg = energy["chg_20d_pct"]
        if trend == "bull":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, +pts, f"Brent crude +{chg:.0f}% (20d) — energy demand rising")
        elif trend == "bear":
            pts = min(6.0, abs(chg) * 0.3)
            for t in _ENERGY_BULL:
                add(t, -pts, f"Brent crude {chg:.0f}% (20d) — energy demand falling")

    # ── Freight contraction signals ───────────────────────────────────────────
    if freight:
        trend = freight["trend"]
        chg = freight["chg_6m_pct"]
        if trend == "bear":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, -pts, f"Cass Freight Index {chg:.0f}% (6m) — freight volumes declining")
        elif trend == "bull":
            pts = min(5.0, abs(chg) * 0.25)
            for t in _FREIGHT_BEAR:
                add(t, +pts, f"Cass Freight Index +{chg:.0f}% (6m) — freight volumes recovering")

    result = []
    for t, d in signals.items():
        direction = "bullish" if d["score"] > 0 else "bearish" if d["score"] < 0 else "neutral"
        result.append(
            {
                "ticker": t,
                "score": round(d["score"], 1),
                "direction": direction,
                "reasons": d["reasons"],
            }
        )
    result.sort(key=lambda x: abs(x["score"]), reverse=False)
    return result

mutants_x__build_sector_signals__mutmut['_mutmut_orig'] = x__build_sector_signals__mutmut_orig # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_1'] = x__build_sector_signals__mutmut_1 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_2'] = x__build_sector_signals__mutmut_2 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_3'] = x__build_sector_signals__mutmut_3 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_4'] = x__build_sector_signals__mutmut_4 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_5'] = x__build_sector_signals__mutmut_5 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_6'] = x__build_sector_signals__mutmut_6 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_7'] = x__build_sector_signals__mutmut_7 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_8'] = x__build_sector_signals__mutmut_8 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_9'] = x__build_sector_signals__mutmut_9 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_10'] = x__build_sector_signals__mutmut_10 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_11'] = x__build_sector_signals__mutmut_11 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_12'] = x__build_sector_signals__mutmut_12 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_13'] = x__build_sector_signals__mutmut_13 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_14'] = x__build_sector_signals__mutmut_14 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_15'] = x__build_sector_signals__mutmut_15 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_16'] = x__build_sector_signals__mutmut_16 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_17'] = x__build_sector_signals__mutmut_17 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_18'] = x__build_sector_signals__mutmut_18 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_19'] = x__build_sector_signals__mutmut_19 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_20'] = x__build_sector_signals__mutmut_20 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_21'] = x__build_sector_signals__mutmut_21 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_22'] = x__build_sector_signals__mutmut_22 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_23'] = x__build_sector_signals__mutmut_23 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_24'] = x__build_sector_signals__mutmut_24 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_25'] = x__build_sector_signals__mutmut_25 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_26'] = x__build_sector_signals__mutmut_26 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_27'] = x__build_sector_signals__mutmut_27 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_28'] = x__build_sector_signals__mutmut_28 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_29'] = x__build_sector_signals__mutmut_29 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_30'] = x__build_sector_signals__mutmut_30 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_31'] = x__build_sector_signals__mutmut_31 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_32'] = x__build_sector_signals__mutmut_32 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_33'] = x__build_sector_signals__mutmut_33 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_34'] = x__build_sector_signals__mutmut_34 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_35'] = x__build_sector_signals__mutmut_35 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_36'] = x__build_sector_signals__mutmut_36 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_37'] = x__build_sector_signals__mutmut_37 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_38'] = x__build_sector_signals__mutmut_38 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_39'] = x__build_sector_signals__mutmut_39 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_40'] = x__build_sector_signals__mutmut_40 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_41'] = x__build_sector_signals__mutmut_41 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_42'] = x__build_sector_signals__mutmut_42 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_43'] = x__build_sector_signals__mutmut_43 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_44'] = x__build_sector_signals__mutmut_44 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_45'] = x__build_sector_signals__mutmut_45 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_46'] = x__build_sector_signals__mutmut_46 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_47'] = x__build_sector_signals__mutmut_47 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_48'] = x__build_sector_signals__mutmut_48 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_49'] = x__build_sector_signals__mutmut_49 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_50'] = x__build_sector_signals__mutmut_50 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_51'] = x__build_sector_signals__mutmut_51 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_52'] = x__build_sector_signals__mutmut_52 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_53'] = x__build_sector_signals__mutmut_53 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_54'] = x__build_sector_signals__mutmut_54 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_55'] = x__build_sector_signals__mutmut_55 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_56'] = x__build_sector_signals__mutmut_56 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_57'] = x__build_sector_signals__mutmut_57 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_58'] = x__build_sector_signals__mutmut_58 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_59'] = x__build_sector_signals__mutmut_59 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_60'] = x__build_sector_signals__mutmut_60 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_61'] = x__build_sector_signals__mutmut_61 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_62'] = x__build_sector_signals__mutmut_62 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_63'] = x__build_sector_signals__mutmut_63 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_64'] = x__build_sector_signals__mutmut_64 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_65'] = x__build_sector_signals__mutmut_65 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_66'] = x__build_sector_signals__mutmut_66 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_67'] = x__build_sector_signals__mutmut_67 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_68'] = x__build_sector_signals__mutmut_68 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_69'] = x__build_sector_signals__mutmut_69 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_70'] = x__build_sector_signals__mutmut_70 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_71'] = x__build_sector_signals__mutmut_71 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_72'] = x__build_sector_signals__mutmut_72 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_73'] = x__build_sector_signals__mutmut_73 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_74'] = x__build_sector_signals__mutmut_74 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_75'] = x__build_sector_signals__mutmut_75 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_76'] = x__build_sector_signals__mutmut_76 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_77'] = x__build_sector_signals__mutmut_77 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_78'] = x__build_sector_signals__mutmut_78 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_79'] = x__build_sector_signals__mutmut_79 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_80'] = x__build_sector_signals__mutmut_80 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_81'] = x__build_sector_signals__mutmut_81 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_82'] = x__build_sector_signals__mutmut_82 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_83'] = x__build_sector_signals__mutmut_83 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_84'] = x__build_sector_signals__mutmut_84 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_85'] = x__build_sector_signals__mutmut_85 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_86'] = x__build_sector_signals__mutmut_86 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_87'] = x__build_sector_signals__mutmut_87 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_88'] = x__build_sector_signals__mutmut_88 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_89'] = x__build_sector_signals__mutmut_89 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_90'] = x__build_sector_signals__mutmut_90 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_91'] = x__build_sector_signals__mutmut_91 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_92'] = x__build_sector_signals__mutmut_92 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_93'] = x__build_sector_signals__mutmut_93 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_94'] = x__build_sector_signals__mutmut_94 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_95'] = x__build_sector_signals__mutmut_95 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_96'] = x__build_sector_signals__mutmut_96 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_97'] = x__build_sector_signals__mutmut_97 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_98'] = x__build_sector_signals__mutmut_98 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_99'] = x__build_sector_signals__mutmut_99 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_100'] = x__build_sector_signals__mutmut_100 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_101'] = x__build_sector_signals__mutmut_101 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_102'] = x__build_sector_signals__mutmut_102 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_103'] = x__build_sector_signals__mutmut_103 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_104'] = x__build_sector_signals__mutmut_104 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_105'] = x__build_sector_signals__mutmut_105 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_106'] = x__build_sector_signals__mutmut_106 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_107'] = x__build_sector_signals__mutmut_107 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_108'] = x__build_sector_signals__mutmut_108 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_109'] = x__build_sector_signals__mutmut_109 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_110'] = x__build_sector_signals__mutmut_110 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_111'] = x__build_sector_signals__mutmut_111 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_112'] = x__build_sector_signals__mutmut_112 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_113'] = x__build_sector_signals__mutmut_113 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_114'] = x__build_sector_signals__mutmut_114 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_115'] = x__build_sector_signals__mutmut_115 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_116'] = x__build_sector_signals__mutmut_116 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_117'] = x__build_sector_signals__mutmut_117 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_118'] = x__build_sector_signals__mutmut_118 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_119'] = x__build_sector_signals__mutmut_119 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_120'] = x__build_sector_signals__mutmut_120 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_121'] = x__build_sector_signals__mutmut_121 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_122'] = x__build_sector_signals__mutmut_122 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_123'] = x__build_sector_signals__mutmut_123 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_124'] = x__build_sector_signals__mutmut_124 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_125'] = x__build_sector_signals__mutmut_125 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_126'] = x__build_sector_signals__mutmut_126 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_127'] = x__build_sector_signals__mutmut_127 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_128'] = x__build_sector_signals__mutmut_128 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_129'] = x__build_sector_signals__mutmut_129 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_130'] = x__build_sector_signals__mutmut_130 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_131'] = x__build_sector_signals__mutmut_131 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_132'] = x__build_sector_signals__mutmut_132 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_133'] = x__build_sector_signals__mutmut_133 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_134'] = x__build_sector_signals__mutmut_134 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_135'] = x__build_sector_signals__mutmut_135 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_136'] = x__build_sector_signals__mutmut_136 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_137'] = x__build_sector_signals__mutmut_137 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_138'] = x__build_sector_signals__mutmut_138 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_139'] = x__build_sector_signals__mutmut_139 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_140'] = x__build_sector_signals__mutmut_140 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_141'] = x__build_sector_signals__mutmut_141 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_142'] = x__build_sector_signals__mutmut_142 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_143'] = x__build_sector_signals__mutmut_143 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_144'] = x__build_sector_signals__mutmut_144 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_145'] = x__build_sector_signals__mutmut_145 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_146'] = x__build_sector_signals__mutmut_146 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_147'] = x__build_sector_signals__mutmut_147 # type: ignore # mutmut generated
mutants_x__build_sector_signals__mutmut['x__build_sector_signals__mutmut_148'] = x__build_sector_signals__mutmut_148 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_supply_chain_signals__mutmut)
async def get_supply_chain_signals() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_orig() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_1() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = None
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_2() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None or now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_3() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["XXresultXX"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_4() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["RESULT"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_5() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_6() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now + _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_7() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["XXtsXX"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_8() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["TS"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_9() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] <= _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_10() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["XXresultXX"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_11() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["RESULT"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_12() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = None
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_13() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        None, _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_14() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), None, return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_15() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=None
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_16() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_17() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_18() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_19() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=False
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_20() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_21() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_22() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = None

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_23() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(None, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_24() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, None, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_25() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, None)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_26() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_27() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_28() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, )

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_29() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = None

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_30() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "XXbrent_crudeXX": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_31() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "BRENT_CRUDE": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_32() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "XXcass_freightXX": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_33() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "CASS_FREIGHT": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_34() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "XXsector_signalsXX": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_35() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "SECTOR_SIGNALS": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_36() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "XXsources_availableXX": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_37() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "SOURCES_AVAILABLE": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_38() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("XXBrent CrudeXX", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_39() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("brent crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_40() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("BRENT CRUDE", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_41() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("XXCass FreightXX", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_42() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("cass freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_43() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("CASS FREIGHT", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_44() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_45() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "XXcached_atXX": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_46() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "CACHED_AT": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_47() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(None),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_48() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = None
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_49() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["XXresultXX"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_50() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["RESULT"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_51() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = None
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_52() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["XXtsXX"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_53() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["TS"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_54() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        None
    )
    return result


async def x_get_supply_chain_signals__mutmut_55() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['XXtrendXX'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_56() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['TREND'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_57() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'XXN/AXX'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_58() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'n/a'} "
        f"freight={freight['trend'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_59() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['XXtrendXX'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_60() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['TREND'] if freight else 'N/A'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_61() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'XXN/AXX'} "
        f"signals={len(sector_signals)}"
    )
    return result


async def x_get_supply_chain_signals__mutmut_62() -> dict:
    """
    Public entrypoint. Returns energy, freight data + per-ticker signal scores.
    Cached for 4 hours.
    """
    global _cache
    now = time.time()
    if _cache["result"] is not None and now - _cache["ts"] < _TTL:
        return _cache["result"]

    energy, freight = await asyncio.gather(
        _fetch_energy_momentum(), _fetch_freight_fred(), return_exceptions=True
    )
    # Treat exceptions as None
    energy = energy if isinstance(energy, dict) else None
    freight = freight if isinstance(freight, dict) else None

    sector_signals = await asyncio.to_thread(_build_sector_signals, energy, freight)

    result = {
        "brent_crude": energy,
        "cass_freight": freight,
        "sector_signals": sector_signals,
        "sources_available": [
            s for s, d in [("Brent Crude", energy), ("Cass Freight", freight)] if d is not None
        ],
        "cached_at": int(now),
    }

    _cache["result"] = result
    _cache["ts"] = now
    log.info(
        f"[supply_chain] energy={energy['trend'] if energy else 'N/A'} "
        f"freight={freight['trend'] if freight else 'n/a'} "
        f"signals={len(sector_signals)}"
    )
    return result

mutants_x_get_supply_chain_signals__mutmut['_mutmut_orig'] = x_get_supply_chain_signals__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_1'] = x_get_supply_chain_signals__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_2'] = x_get_supply_chain_signals__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_3'] = x_get_supply_chain_signals__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_4'] = x_get_supply_chain_signals__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_5'] = x_get_supply_chain_signals__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_6'] = x_get_supply_chain_signals__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_7'] = x_get_supply_chain_signals__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_8'] = x_get_supply_chain_signals__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_9'] = x_get_supply_chain_signals__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_10'] = x_get_supply_chain_signals__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_11'] = x_get_supply_chain_signals__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_12'] = x_get_supply_chain_signals__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_13'] = x_get_supply_chain_signals__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_14'] = x_get_supply_chain_signals__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_15'] = x_get_supply_chain_signals__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_16'] = x_get_supply_chain_signals__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_17'] = x_get_supply_chain_signals__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_18'] = x_get_supply_chain_signals__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_19'] = x_get_supply_chain_signals__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_20'] = x_get_supply_chain_signals__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_21'] = x_get_supply_chain_signals__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_22'] = x_get_supply_chain_signals__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_23'] = x_get_supply_chain_signals__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_24'] = x_get_supply_chain_signals__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_25'] = x_get_supply_chain_signals__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_26'] = x_get_supply_chain_signals__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_27'] = x_get_supply_chain_signals__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_28'] = x_get_supply_chain_signals__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_29'] = x_get_supply_chain_signals__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_30'] = x_get_supply_chain_signals__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_31'] = x_get_supply_chain_signals__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_32'] = x_get_supply_chain_signals__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_33'] = x_get_supply_chain_signals__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_34'] = x_get_supply_chain_signals__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_35'] = x_get_supply_chain_signals__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_36'] = x_get_supply_chain_signals__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_37'] = x_get_supply_chain_signals__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_38'] = x_get_supply_chain_signals__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_39'] = x_get_supply_chain_signals__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_40'] = x_get_supply_chain_signals__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_41'] = x_get_supply_chain_signals__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_42'] = x_get_supply_chain_signals__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_43'] = x_get_supply_chain_signals__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_44'] = x_get_supply_chain_signals__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_45'] = x_get_supply_chain_signals__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_46'] = x_get_supply_chain_signals__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_47'] = x_get_supply_chain_signals__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_48'] = x_get_supply_chain_signals__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_49'] = x_get_supply_chain_signals__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_50'] = x_get_supply_chain_signals__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_51'] = x_get_supply_chain_signals__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_52'] = x_get_supply_chain_signals__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_53'] = x_get_supply_chain_signals__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_54'] = x_get_supply_chain_signals__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_55'] = x_get_supply_chain_signals__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_56'] = x_get_supply_chain_signals__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_57'] = x_get_supply_chain_signals__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_58'] = x_get_supply_chain_signals__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_59'] = x_get_supply_chain_signals__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_60'] = x_get_supply_chain_signals__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_61'] = x_get_supply_chain_signals__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_supply_chain_signals__mutmut['x_get_supply_chain_signals__mutmut_62'] = x_get_supply_chain_signals__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_supply_chain_score__mutmut)
def get_supply_chain_score(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_orig(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_1(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_2(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 1.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_3(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get(None, []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_4(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", None):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_5(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get([]):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_6(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", ):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_7(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("XXsector_signalsXX", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_8(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("SECTOR_SIGNALS", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_9(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["XXtickerXX"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_10(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["TICKER"] == ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_11(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] != ticker:
            return sig["score"]
    return 0.0


def x_get_supply_chain_score__mutmut_12(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["XXscoreXX"]
    return 0.0


def x_get_supply_chain_score__mutmut_13(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["SCORE"]
    return 0.0


def x_get_supply_chain_score__mutmut_14(ticker: str, supply_chain_ctx: dict | None) -> float:
    """
    Convenience function for signal_engine — returns supply chain score for a ticker.
    Score range: approximately −6 to +6 points.
    """
    if not supply_chain_ctx:
        return 0.0
    for sig in supply_chain_ctx.get("sector_signals", []):
        if sig["ticker"] == ticker:
            return sig["score"]
    return 1.0

mutants_x_get_supply_chain_score__mutmut['_mutmut_orig'] = x_get_supply_chain_score__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_1'] = x_get_supply_chain_score__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_2'] = x_get_supply_chain_score__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_3'] = x_get_supply_chain_score__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_4'] = x_get_supply_chain_score__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_5'] = x_get_supply_chain_score__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_6'] = x_get_supply_chain_score__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_7'] = x_get_supply_chain_score__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_8'] = x_get_supply_chain_score__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_9'] = x_get_supply_chain_score__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_10'] = x_get_supply_chain_score__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_11'] = x_get_supply_chain_score__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_12'] = x_get_supply_chain_score__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_13'] = x_get_supply_chain_score__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_supply_chain_score__mutmut['x_get_supply_chain_score__mutmut_14'] = x_get_supply_chain_score__mutmut_14 # type: ignore # mutmut generated


# ── Supply Chain Graph Propagation ───────────────────────────────────────────
# Supplier → customer lead-lag relationships. When a major supplier reports
# a strong beat / miss, it carries predictive information for downstream customers.
#
# Research basis: semiconductor cycle propagates TSM → NVDA/AMD/QCOM with a 1–4
# week lag; energy costs propagate XOM/CVX → transportation/airlines; steel
# costs propagate SCCO/FCX → auto/construction; cloud capex propagates
# MSFT/AMZN/GOOGL → NVDA/AMD/AMAT (chip demand surge).
#
# Score is applied as a small (+3 to +6 pt) supplemental boost / penalty when
# a top-tier supplier has had a recent signal in the opposite direction.

_SUPPLIER_CUSTOMER_MAP: dict[str, list[str]] = {
    # Semiconductors: foundry → chip designers
    "TSM": ["NVDA", "AMD", "QCOM", "AAPL", "ARM", "MRVL", "AVGO"],
    "AMAT": ["NVDA", "AMD", "INTC", "TSM", "MU", "KLAC", "LRCX"],
    "KLAC": ["TSM", "AMAT", "MU", "NVDA", "SNPS", "CDNS"],
    "LRCX": ["TSM", "MU", "NVDA", "AMD", "AMAT"],
    # Cloud hyperscalers → GPU/infrastructure demand
    "MSFT": ["NVDA", "AMD", "AMAT", "DELL", "HPE"],
    "AMZN": ["NVDA", "AMD", "ARM", "AMAT", "UPS", "FDX"],
    "GOOGL": ["NVDA", "AMD", "ARM", "AMAT"],
    # Energy → transportation/airlines
    "XOM": ["UPS", "UNP", "DAL", "AAL"],
    "CVX": ["UPS", "UNP", "DAL", "AAL"],
    # Steel/copper → auto/construction
    "FCX": ["GM", "F", "CAT", "DE", "HON", "ETN"],
    "SCCO": ["GM", "CAT", "DE", "HON"],
    "WMT": ["UPS", "FDX", "PG", "KO", "PEP"],
}

# Direction of signal propagation (+1 = supplier bull is customer bull, -1 = inverse)
_PROPAGATION_DIRECTION: dict[str, int] = {
    "TSM": +1,
    "AMAT": +1,
    "KLAC": +1,
    "LRCX": +1,
    "MSFT": +1,
    "AMZN": +1,
    "GOOGL": +1,
    "XOM": -1,
    "CVX": -1,  # energy costs → headwind for transportation
    "FCX": -1,
    "SCCO": -1,  # materials costs → headwind for manufacturers
    "WMT": +1,
}
mutants_x_get_supply_chain_propagation_score__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_supply_chain_propagation_score__mutmut)
def get_supply_chain_propagation_score(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_orig(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_1(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = None
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_2(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 1.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_3(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = None

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_4(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_5(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            break
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_6(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = None
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_7(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(None)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_8(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_9(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            break

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_10(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = None
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_11(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get(None, "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_12(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", None)
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_13(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_14(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", )
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_15(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("XXactionXX", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_16(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("ACTION", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_17(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "XXHOLDXX")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_18(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "hold")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_19(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = None
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_20(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get(None, 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_21(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", None)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_22(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get(0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_23(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", )
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_24(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("XXconfidenceXX", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_25(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("CONFIDENCE", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_26(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 1)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_27(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" and s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_28(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action != "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_29(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "XXHOLDXX" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_30(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "hold" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_31(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf <= 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_32(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 66:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_33(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            break  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_34(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = None
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_35(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(None, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_36(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, None)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_37(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(+1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_38(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, )
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_39(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, -1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_40(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +2)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_41(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = None  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_42(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 / direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_43(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 / 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_44(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) * 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_45(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf + 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_46(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 61) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_47(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 101 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_48(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 31 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_49(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action != "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_50(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "XXSELLXX":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_51(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "sell":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_52(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost = -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_53(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost /= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_54(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= +1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_55(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -2
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_56(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = None
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_57(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(None, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_58(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, None)
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_59(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_60(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, )
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_61(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(+6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_62(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-7.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_63(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(None, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_64(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, None))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_65(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_66(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, ))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_67(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(7.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_68(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(None) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_69(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) <= 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_70(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 2.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_71(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            break

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_72(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost = capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_73(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost -= capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_74(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            None
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_75(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'XXtailwindXX' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_76(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'TAILWIND' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_77(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped >= 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_78(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 1 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_79(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'XXheadwindXX'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_80(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'HEADWIND'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_81(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_82(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 1.0, ""
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_83(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, "XXXX"
    return round(boost, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_84(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(None, 1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_85(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, None), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_86(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(1), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_87(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, ), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_88(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 2), " | ".join(reasons)


def x_get_supply_chain_propagation_score__mutmut_89(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), " | ".join(None)


def x_get_supply_chain_propagation_score__mutmut_90(
    ticker: str,
    all_signals: dict[str, dict],
) -> tuple[float, str]:
    """
    Check if a key supplier of `ticker` has recently fired a strong signal.
    If so, propagate a fraction of that signal as a lead-lag boost/penalty.

    Args:
        ticker:       Target ticker to score.
        all_signals:  {ticker: signal_dict} from the current scan cycle.
                      Signal dict must have keys: action, confidence.

    Returns:
        (score_delta, reason) — score_delta is 0 if no applicable supplier signal.
    """
    boost = 0.0
    reasons = []

    for supplier, customers in _SUPPLIER_CUSTOMER_MAP.items():
        if ticker not in customers:
            continue
        supplier_sig = all_signals.get(supplier)
        if not supplier_sig:
            continue

        s_action = supplier_sig.get("action", "HOLD")
        s_conf = supplier_sig.get("confidence", 0)
        if s_action == "HOLD" or s_conf < 65:
            continue  # only propagate strong supplier signals

        direction = _PROPAGATION_DIRECTION.get(supplier, +1)
        # Propagate 20% of the supplier's signal strength (capped at ±6)
        raw_boost = (s_conf - 60) / 100 * 30 * direction  # 65% conf → +1.5 pts
        if s_action == "SELL":
            raw_boost *= -1
        capped = max(-6.0, min(6.0, raw_boost))
        if abs(capped) < 1.0:
            continue

        boost += capped
        reasons.append(
            f"{supplier} {s_action} ({s_conf:.0f}% conf) → {'tailwind' if capped > 0 else 'headwind'} for {ticker}"
        )

    if not reasons:
        return 0.0, ""
    return round(boost, 1), "XX | XX".join(reasons)

mutants_x_get_supply_chain_propagation_score__mutmut['_mutmut_orig'] = x_get_supply_chain_propagation_score__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_1'] = x_get_supply_chain_propagation_score__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_2'] = x_get_supply_chain_propagation_score__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_3'] = x_get_supply_chain_propagation_score__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_4'] = x_get_supply_chain_propagation_score__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_5'] = x_get_supply_chain_propagation_score__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_6'] = x_get_supply_chain_propagation_score__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_7'] = x_get_supply_chain_propagation_score__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_8'] = x_get_supply_chain_propagation_score__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_9'] = x_get_supply_chain_propagation_score__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_10'] = x_get_supply_chain_propagation_score__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_11'] = x_get_supply_chain_propagation_score__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_12'] = x_get_supply_chain_propagation_score__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_13'] = x_get_supply_chain_propagation_score__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_14'] = x_get_supply_chain_propagation_score__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_15'] = x_get_supply_chain_propagation_score__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_16'] = x_get_supply_chain_propagation_score__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_17'] = x_get_supply_chain_propagation_score__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_18'] = x_get_supply_chain_propagation_score__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_19'] = x_get_supply_chain_propagation_score__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_20'] = x_get_supply_chain_propagation_score__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_21'] = x_get_supply_chain_propagation_score__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_22'] = x_get_supply_chain_propagation_score__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_23'] = x_get_supply_chain_propagation_score__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_24'] = x_get_supply_chain_propagation_score__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_25'] = x_get_supply_chain_propagation_score__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_26'] = x_get_supply_chain_propagation_score__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_27'] = x_get_supply_chain_propagation_score__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_28'] = x_get_supply_chain_propagation_score__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_29'] = x_get_supply_chain_propagation_score__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_30'] = x_get_supply_chain_propagation_score__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_31'] = x_get_supply_chain_propagation_score__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_32'] = x_get_supply_chain_propagation_score__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_33'] = x_get_supply_chain_propagation_score__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_34'] = x_get_supply_chain_propagation_score__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_35'] = x_get_supply_chain_propagation_score__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_36'] = x_get_supply_chain_propagation_score__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_37'] = x_get_supply_chain_propagation_score__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_38'] = x_get_supply_chain_propagation_score__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_39'] = x_get_supply_chain_propagation_score__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_40'] = x_get_supply_chain_propagation_score__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_41'] = x_get_supply_chain_propagation_score__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_42'] = x_get_supply_chain_propagation_score__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_43'] = x_get_supply_chain_propagation_score__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_44'] = x_get_supply_chain_propagation_score__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_45'] = x_get_supply_chain_propagation_score__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_46'] = x_get_supply_chain_propagation_score__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_47'] = x_get_supply_chain_propagation_score__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_48'] = x_get_supply_chain_propagation_score__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_49'] = x_get_supply_chain_propagation_score__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_50'] = x_get_supply_chain_propagation_score__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_51'] = x_get_supply_chain_propagation_score__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_52'] = x_get_supply_chain_propagation_score__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_53'] = x_get_supply_chain_propagation_score__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_54'] = x_get_supply_chain_propagation_score__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_55'] = x_get_supply_chain_propagation_score__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_56'] = x_get_supply_chain_propagation_score__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_57'] = x_get_supply_chain_propagation_score__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_58'] = x_get_supply_chain_propagation_score__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_59'] = x_get_supply_chain_propagation_score__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_60'] = x_get_supply_chain_propagation_score__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_61'] = x_get_supply_chain_propagation_score__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_62'] = x_get_supply_chain_propagation_score__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_63'] = x_get_supply_chain_propagation_score__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_64'] = x_get_supply_chain_propagation_score__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_65'] = x_get_supply_chain_propagation_score__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_66'] = x_get_supply_chain_propagation_score__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_67'] = x_get_supply_chain_propagation_score__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_68'] = x_get_supply_chain_propagation_score__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_69'] = x_get_supply_chain_propagation_score__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_70'] = x_get_supply_chain_propagation_score__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_71'] = x_get_supply_chain_propagation_score__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_72'] = x_get_supply_chain_propagation_score__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_73'] = x_get_supply_chain_propagation_score__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_74'] = x_get_supply_chain_propagation_score__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_75'] = x_get_supply_chain_propagation_score__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_76'] = x_get_supply_chain_propagation_score__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_77'] = x_get_supply_chain_propagation_score__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_78'] = x_get_supply_chain_propagation_score__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_79'] = x_get_supply_chain_propagation_score__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_80'] = x_get_supply_chain_propagation_score__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_81'] = x_get_supply_chain_propagation_score__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_82'] = x_get_supply_chain_propagation_score__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_83'] = x_get_supply_chain_propagation_score__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_84'] = x_get_supply_chain_propagation_score__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_85'] = x_get_supply_chain_propagation_score__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_86'] = x_get_supply_chain_propagation_score__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_87'] = x_get_supply_chain_propagation_score__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_88'] = x_get_supply_chain_propagation_score__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_89'] = x_get_supply_chain_propagation_score__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_supply_chain_propagation_score__mutmut['x_get_supply_chain_propagation_score__mutmut_90'] = x_get_supply_chain_propagation_score__mutmut_90 # type: ignore # mutmut generated
