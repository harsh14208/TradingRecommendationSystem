"""
Polygon.io News — Drop-in replacement for RSS scraper.

Uses Polygon.io v2/reference/news which is accessible on the free plan.
Returns structured news with publisher, tickers, and title — we score sentiment
ourselves using keyword matching (no pre-scored API sentiment field available
at this tier, but signal is still better than RSS due to latency <5min).

Latency vs RSS: ~2–5 minutes vs 15–30 minutes.
Cache: 5 minutes per ticker.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

import aiohttp
from services.http_client import get_ssl_context, shared_session

log = logging.getLogger("signal.trade.polygon_news")

_cache: dict[str, dict] = {}
_TTL = 300  # 5-minute per-ticker cache
_BASE = "https://api.polygon.io/v2/reference/news"

# Simple keyword-based sentiment scoring
_BULL_WORDS = {
    "beat",
    "beats",
    "record",
    "surge",
    "soars",
    "rises",
    "gain",
    "profit",
    "revenue",
    "growth",
    "strong",
    "upgrade",
    "buy",
    "bullish",
    "outperform",
    "raised",
    "raises",
    "guidance",
    "exceeds",
    "acquisition",
    "buyback",
    "dividend",
    "partnership",
    "deal",
    "approved",
    "expansion",
}
_BEAR_WORDS = {
    "miss",
    "misses",
    "cut",
    "cuts",
    "falls",
    "drops",
    "decline",
    "loss",
    "warning",
    "downgrade",
    "sell",
    "bearish",
    "underperform",
    "layoff",
    "recall",
    "lawsuit",
    "investigation",
    "fraud",
    "debt",
    "bankruptcy",
    "guidance",
    "below",
    "disappoints",
    "withdraws",
    "delays",
}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__score_headline__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__score_headline__mutmut)
def _score_headline(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_orig(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_1(title: str, description: str = "XXXX") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_2(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = None
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_3(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).upper()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_4(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " - description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_5(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title - " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_6(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + "XX XX" + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_7(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = None
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_8(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(None)
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_9(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = None
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_10(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = None
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_11(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = None
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_12(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) / 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_13(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull + bear) * 0.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_14(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 1.1
    return max(-0.6, min(0.6, raw))


def x__score_headline__mutmut_15(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(None, min(0.6, raw))


def x__score_headline__mutmut_16(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, None)


def x__score_headline__mutmut_17(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(min(0.6, raw))


def x__score_headline__mutmut_18(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, )


def x__score_headline__mutmut_19(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(+0.6, min(0.6, raw))


def x__score_headline__mutmut_20(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-1.6, min(0.6, raw))


def x__score_headline__mutmut_21(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(None, raw))


def x__score_headline__mutmut_22(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, None))


def x__score_headline__mutmut_23(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(raw))


def x__score_headline__mutmut_24(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(0.6, ))


def x__score_headline__mutmut_25(title: str, description: str = "") -> float:
    """Keyword-based sentiment: +0.1 per bull word, -0.1 per bear word, capped ±0.6."""
    text = (title + " " + description).lower()
    words = set(text.split())
    bull = len(words & _BULL_WORDS)
    bear = len(words & _BEAR_WORDS)
    raw = (bull - bear) * 0.1
    return max(-0.6, min(1.6, raw))

mutants_x__score_headline__mutmut['_mutmut_orig'] = x__score_headline__mutmut_orig # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_1'] = x__score_headline__mutmut_1 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_2'] = x__score_headline__mutmut_2 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_3'] = x__score_headline__mutmut_3 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_4'] = x__score_headline__mutmut_4 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_5'] = x__score_headline__mutmut_5 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_6'] = x__score_headline__mutmut_6 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_7'] = x__score_headline__mutmut_7 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_8'] = x__score_headline__mutmut_8 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_9'] = x__score_headline__mutmut_9 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_10'] = x__score_headline__mutmut_10 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_11'] = x__score_headline__mutmut_11 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_12'] = x__score_headline__mutmut_12 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_13'] = x__score_headline__mutmut_13 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_14'] = x__score_headline__mutmut_14 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_15'] = x__score_headline__mutmut_15 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_16'] = x__score_headline__mutmut_16 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_17'] = x__score_headline__mutmut_17 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_18'] = x__score_headline__mutmut_18 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_19'] = x__score_headline__mutmut_19 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_20'] = x__score_headline__mutmut_20 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_21'] = x__score_headline__mutmut_21 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_22'] = x__score_headline__mutmut_22 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_23'] = x__score_headline__mutmut_23 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_24'] = x__score_headline__mutmut_24 # type: ignore # mutmut generated
mutants_x__score_headline__mutmut['x__score_headline__mutmut_25'] = x__score_headline__mutmut_25 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__age_decay__mutmut)
def _age_decay(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_orig(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_1(published_utc: str) -> float:
    try:
        pub = None
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_2(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(None)
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_3(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace(None, "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_4(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", None))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_5(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_6(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", ))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_7(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("XXZXX", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_8(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_9(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "XX+00:00XX"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_10(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = None
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_11(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() * 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_12(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) + pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_13(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(None) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_14(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3601
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_15(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h <= 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_16(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 3:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_17(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 2.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_18(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h <= 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_19(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 9:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_20(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 1.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_21(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h <= 24:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_22(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 25:
            return 0.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_23(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 1.4
        return 0.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_24(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 1.15
    except Exception:
        return 0.5


def x__age_decay__mutmut_25(published_utc: str) -> float:
    try:
        pub = datetime.fromisoformat(published_utc.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        if age_h < 2:
            return 1.0
        if age_h < 8:
            return 0.7
        if age_h < 24:
            return 0.4
        return 0.15
    except Exception:
        return 1.5

mutants_x__age_decay__mutmut['_mutmut_orig'] = x__age_decay__mutmut_orig # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_1'] = x__age_decay__mutmut_1 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_2'] = x__age_decay__mutmut_2 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_3'] = x__age_decay__mutmut_3 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_4'] = x__age_decay__mutmut_4 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_5'] = x__age_decay__mutmut_5 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_6'] = x__age_decay__mutmut_6 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_7'] = x__age_decay__mutmut_7 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_8'] = x__age_decay__mutmut_8 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_9'] = x__age_decay__mutmut_9 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_10'] = x__age_decay__mutmut_10 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_11'] = x__age_decay__mutmut_11 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_12'] = x__age_decay__mutmut_12 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_13'] = x__age_decay__mutmut_13 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_14'] = x__age_decay__mutmut_14 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_15'] = x__age_decay__mutmut_15 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_16'] = x__age_decay__mutmut_16 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_17'] = x__age_decay__mutmut_17 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_18'] = x__age_decay__mutmut_18 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_19'] = x__age_decay__mutmut_19 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_20'] = x__age_decay__mutmut_20 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_21'] = x__age_decay__mutmut_21 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_22'] = x__age_decay__mutmut_22 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_23'] = x__age_decay__mutmut_23 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_24'] = x__age_decay__mutmut_24 # type: ignore # mutmut generated
mutants_x__age_decay__mutmut['x__age_decay__mutmut_25'] = x__age_decay__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_benzinga_news__mutmut)
async def get_benzinga_news(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_orig(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_1(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = None
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_2(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache or now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_3(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker not in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_4(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now + _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_5(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["XXtsXX"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_6(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["TS"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_7(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] <= _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_8(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["XXarticlesXX"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_9(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["ARTICLES"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_10(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = None
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_11(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv(None)
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_12(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("XXMASSIVE_API_KEYXX")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_13(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("massive_api_key")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_14(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_15(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = None
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_16(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"XXtickerXX": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_17(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"TICKER": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_18(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "XXlimitXX": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_19(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "LIMIT": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_20(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 11, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_21(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "XXorderXX": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_22(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "ORDER": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_23(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "XXdescXX", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_24(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "DESC", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_25(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "XXsortXX": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_26(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "SORT": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_27(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "XXpublished_utcXX", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_28(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "PUBLISHED_UTC", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_29(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "XXapiKeyXX": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_30(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apikey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_31(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "APIKEY": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_32(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = None

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_33(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(None, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_34(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=None, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_35(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_36(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=None) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_37(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_38(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_39(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_40(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_41(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=None)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_42(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=9)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_43(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_44(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 201:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_45(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = None
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_46(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = None
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_47(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") and []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_48(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get(None) or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_49(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("XXresultsXX") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_50(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("RESULTS") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_51(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(None)
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_52(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = None
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_53(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = None
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_54(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get(None, "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_55(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", None)
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_56(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_57(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", )
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_58(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("XXpublished_utcXX", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_59(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("PUBLISHED_UTC", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_60(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "XXXX")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_61(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = None
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_62(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(None, a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_63(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), None)
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_64(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_65(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), )
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_66(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get(None, ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_67(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", None), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_68(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get(""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_69(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_70(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("XXtitleXX", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_71(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("TITLE", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_72(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", "XXXX"), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_73(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get(None, ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_74(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", None))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_75(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get(""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_76(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_77(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("XXdescriptionXX", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_78(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("DESCRIPTION", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_79(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", "XXXX"))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_80(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = None
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_81(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(None)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_82(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            None
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_83(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "XXheadlineXX": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_84(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "HEADLINE": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_85(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get(None, ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_86(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", None),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_87(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get(""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_88(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_89(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("XXtitleXX", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_90(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("TITLE", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_91(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", "XXXX"),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_92(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "XXsentimentXX": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_93(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "SENTIMENT": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_94(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(None, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_95(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, None),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_96(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_97(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, ),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_98(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent / decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_99(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 4),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_100(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "XXraw_sentimentXX": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_101(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "RAW_SENTIMENT": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_102(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(None, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_103(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, None),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_104(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_105(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, ),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_106(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 4),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_107(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "XXurlXX": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_108(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "URL": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_109(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get(None, ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_110(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", None),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_111(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get(""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_112(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_113(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("XXarticle_urlXX", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_114(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("ARTICLE_URL", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_115(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", "XXXX"),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_116(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "XXpublished_atXX": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_117(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "PUBLISHED_AT": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_118(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "XXsourceXX": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_119(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "SOURCE": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_120(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get(None, "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_121(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", None),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_122(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_123(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", ),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_124(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") and {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_125(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get(None) or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_126(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("XXpublisherXX") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_127(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("PUBLISHER") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_128(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("XXnameXX", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_129(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("NAME", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_130(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "XXNewsXX"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_131(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "news"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_132(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "NEWS"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_133(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "XXage_decayXX": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_134(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "AGE_DECAY": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_135(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(None, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_136(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, None),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_137(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(2),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_138(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, ),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_139(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 3),
            }
        )

    _cache[ticker] = {"articles": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_140(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = None
    return articles


async def x_get_benzinga_news__mutmut_141(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"XXarticlesXX": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_142(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"ARTICLES": articles, "ts": now}
    return articles


async def x_get_benzinga_news__mutmut_143(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "XXtsXX": now}
    return articles


async def x_get_benzinga_news__mutmut_144(ticker: str) -> list[dict]:
    """
    Fetch recent news for a ticker from Polygon.io.
    Returns list of {headline, sentiment, url, published_at, source}.
    """
    now = time.time()
    if ticker in _cache and now - _cache[ticker]["ts"] < _TTL:
        return _cache[ticker]["articles"]

    api_key = os.getenv("MASSIVE_API_KEY")
    if not api_key:
        return []

    params = {"ticker": ticker, "limit": 10, "order": "desc", "sort": "published_utc", "apiKey": api_key}
    ssl_ctx = get_ssl_context()

    try:
        async with shared_session() as session:
            async with session.get(_BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                raw = data.get("results") or []
    except Exception as e:
        log.debug(f"[polygon_news] {ticker}: {e}")
        return []

    articles = []
    for a in raw:
        pub = a.get("published_utc", "")
        raw_sent = _score_headline(a.get("title", ""), a.get("description", ""))
        decay = _age_decay(pub)
        articles.append(
            {
                "headline": a.get("title", ""),
                "sentiment": round(raw_sent * decay, 3),
                "raw_sentiment": round(raw_sent, 3),
                "url": a.get("article_url", ""),
                "published_at": pub,
                "source": (a.get("publisher") or {}).get("name", "News"),
                "age_decay": round(decay, 2),
            }
        )

    _cache[ticker] = {"articles": articles, "TS": now}
    return articles

mutants_x_get_benzinga_news__mutmut['_mutmut_orig'] = x_get_benzinga_news__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_1'] = x_get_benzinga_news__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_2'] = x_get_benzinga_news__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_3'] = x_get_benzinga_news__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_4'] = x_get_benzinga_news__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_5'] = x_get_benzinga_news__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_6'] = x_get_benzinga_news__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_7'] = x_get_benzinga_news__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_8'] = x_get_benzinga_news__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_9'] = x_get_benzinga_news__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_10'] = x_get_benzinga_news__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_11'] = x_get_benzinga_news__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_12'] = x_get_benzinga_news__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_13'] = x_get_benzinga_news__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_14'] = x_get_benzinga_news__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_15'] = x_get_benzinga_news__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_16'] = x_get_benzinga_news__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_17'] = x_get_benzinga_news__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_18'] = x_get_benzinga_news__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_19'] = x_get_benzinga_news__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_20'] = x_get_benzinga_news__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_21'] = x_get_benzinga_news__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_22'] = x_get_benzinga_news__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_23'] = x_get_benzinga_news__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_24'] = x_get_benzinga_news__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_25'] = x_get_benzinga_news__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_26'] = x_get_benzinga_news__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_27'] = x_get_benzinga_news__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_28'] = x_get_benzinga_news__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_29'] = x_get_benzinga_news__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_30'] = x_get_benzinga_news__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_31'] = x_get_benzinga_news__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_32'] = x_get_benzinga_news__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_33'] = x_get_benzinga_news__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_34'] = x_get_benzinga_news__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_35'] = x_get_benzinga_news__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_36'] = x_get_benzinga_news__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_37'] = x_get_benzinga_news__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_38'] = x_get_benzinga_news__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_39'] = x_get_benzinga_news__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_40'] = x_get_benzinga_news__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_41'] = x_get_benzinga_news__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_42'] = x_get_benzinga_news__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_43'] = x_get_benzinga_news__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_44'] = x_get_benzinga_news__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_45'] = x_get_benzinga_news__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_46'] = x_get_benzinga_news__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_47'] = x_get_benzinga_news__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_48'] = x_get_benzinga_news__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_49'] = x_get_benzinga_news__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_50'] = x_get_benzinga_news__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_51'] = x_get_benzinga_news__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_52'] = x_get_benzinga_news__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_53'] = x_get_benzinga_news__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_54'] = x_get_benzinga_news__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_55'] = x_get_benzinga_news__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_56'] = x_get_benzinga_news__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_57'] = x_get_benzinga_news__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_58'] = x_get_benzinga_news__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_59'] = x_get_benzinga_news__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_60'] = x_get_benzinga_news__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_61'] = x_get_benzinga_news__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_62'] = x_get_benzinga_news__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_63'] = x_get_benzinga_news__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_64'] = x_get_benzinga_news__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_65'] = x_get_benzinga_news__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_66'] = x_get_benzinga_news__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_67'] = x_get_benzinga_news__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_68'] = x_get_benzinga_news__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_69'] = x_get_benzinga_news__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_70'] = x_get_benzinga_news__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_71'] = x_get_benzinga_news__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_72'] = x_get_benzinga_news__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_73'] = x_get_benzinga_news__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_74'] = x_get_benzinga_news__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_75'] = x_get_benzinga_news__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_76'] = x_get_benzinga_news__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_77'] = x_get_benzinga_news__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_78'] = x_get_benzinga_news__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_79'] = x_get_benzinga_news__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_80'] = x_get_benzinga_news__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_81'] = x_get_benzinga_news__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_82'] = x_get_benzinga_news__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_83'] = x_get_benzinga_news__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_84'] = x_get_benzinga_news__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_85'] = x_get_benzinga_news__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_86'] = x_get_benzinga_news__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_87'] = x_get_benzinga_news__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_88'] = x_get_benzinga_news__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_89'] = x_get_benzinga_news__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_90'] = x_get_benzinga_news__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_91'] = x_get_benzinga_news__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_92'] = x_get_benzinga_news__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_93'] = x_get_benzinga_news__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_94'] = x_get_benzinga_news__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_95'] = x_get_benzinga_news__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_96'] = x_get_benzinga_news__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_97'] = x_get_benzinga_news__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_98'] = x_get_benzinga_news__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_99'] = x_get_benzinga_news__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_100'] = x_get_benzinga_news__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_101'] = x_get_benzinga_news__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_102'] = x_get_benzinga_news__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_103'] = x_get_benzinga_news__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_104'] = x_get_benzinga_news__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_105'] = x_get_benzinga_news__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_106'] = x_get_benzinga_news__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_107'] = x_get_benzinga_news__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_108'] = x_get_benzinga_news__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_109'] = x_get_benzinga_news__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_110'] = x_get_benzinga_news__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_111'] = x_get_benzinga_news__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_112'] = x_get_benzinga_news__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_113'] = x_get_benzinga_news__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_114'] = x_get_benzinga_news__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_115'] = x_get_benzinga_news__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_116'] = x_get_benzinga_news__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_117'] = x_get_benzinga_news__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_118'] = x_get_benzinga_news__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_119'] = x_get_benzinga_news__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_120'] = x_get_benzinga_news__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_121'] = x_get_benzinga_news__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_122'] = x_get_benzinga_news__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_123'] = x_get_benzinga_news__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_124'] = x_get_benzinga_news__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_125'] = x_get_benzinga_news__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_126'] = x_get_benzinga_news__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_127'] = x_get_benzinga_news__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_128'] = x_get_benzinga_news__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_129'] = x_get_benzinga_news__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_130'] = x_get_benzinga_news__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_131'] = x_get_benzinga_news__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_132'] = x_get_benzinga_news__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_133'] = x_get_benzinga_news__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_134'] = x_get_benzinga_news__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_135'] = x_get_benzinga_news__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_136'] = x_get_benzinga_news__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_137'] = x_get_benzinga_news__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_138'] = x_get_benzinga_news__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_139'] = x_get_benzinga_news__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_140'] = x_get_benzinga_news__mutmut_140 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_141'] = x_get_benzinga_news__mutmut_141 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_142'] = x_get_benzinga_news__mutmut_142 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_143'] = x_get_benzinga_news__mutmut_143 # type: ignore # mutmut generated
mutants_x_get_benzinga_news__mutmut['x_get_benzinga_news__mutmut_144'] = x_get_benzinga_news__mutmut_144 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_score_benzinga_news__mutmut)
def score_benzinga_news(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_orig(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_1(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_2(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 1.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_3(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "XXXX", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_4(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "XXneutralXX"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_5(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "NEUTRAL"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_6(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = None
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_7(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) * len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_8(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(None) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_9(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["XXsentimentXX"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_10(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["SENTIMENT"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_11(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = None
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_12(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(None, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_13(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=None, default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_14(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_15(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_16(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), )
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_17(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: None, default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_18(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(None), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_19(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["XXsentimentXX"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_20(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["SENTIMENT"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_21(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = None
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_22(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["XXheadlineXX"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_23(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["HEADLINE"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_24(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else "XXXX"
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_25(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net > 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_26(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 1.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_27(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return -4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_28(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +5.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_29(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "XXBullishXX"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_30(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_31(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "BULLISH"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_32(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net > 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_33(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 1.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_34(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return -2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_35(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +3.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_36(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "XXMildly BullishXX"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_37(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "mildly bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_38(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "MILDLY BULLISH"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_39(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net < -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_40(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= +0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_41(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -1.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_42(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return +4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_43(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -5.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_44(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "XXBearishXX"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_45(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_46(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "BEARISH"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_47(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net < -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_48(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= +0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_49(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -1.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_50(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return +2.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_51(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -3.0, headline, "Mildly Bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_52(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "XXMildly BearishXX"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_53(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "mildly bearish"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_54(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "MILDLY BEARISH"
    return 0.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_55(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 1.0, headline, "Neutral"


def x_score_benzinga_news__mutmut_56(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "XXNeutralXX"


def x_score_benzinga_news__mutmut_57(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "neutral"


def x_score_benzinga_news__mutmut_58(articles: list[dict]) -> tuple[float, str, str]:
    """Same interface as before: (score_pts, headline, label)."""
    if not articles:
        return 0.0, "", "neutral"
    net = sum(a["sentiment"] for a in articles) / len(articles)
    best = max(articles, key=lambda a: abs(a["sentiment"]), default=None)
    headline = best["headline"] if best else ""
    if net >= 0.3:
        return +4.0, headline, "Bullish"
    if net >= 0.1:
        return +2.0, headline, "Mildly Bullish"
    if net <= -0.3:
        return -4.0, headline, "Bearish"
    if net <= -0.1:
        return -2.0, headline, "Mildly Bearish"
    return 0.0, headline, "NEUTRAL"

mutants_x_score_benzinga_news__mutmut['_mutmut_orig'] = x_score_benzinga_news__mutmut_orig # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_1'] = x_score_benzinga_news__mutmut_1 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_2'] = x_score_benzinga_news__mutmut_2 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_3'] = x_score_benzinga_news__mutmut_3 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_4'] = x_score_benzinga_news__mutmut_4 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_5'] = x_score_benzinga_news__mutmut_5 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_6'] = x_score_benzinga_news__mutmut_6 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_7'] = x_score_benzinga_news__mutmut_7 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_8'] = x_score_benzinga_news__mutmut_8 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_9'] = x_score_benzinga_news__mutmut_9 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_10'] = x_score_benzinga_news__mutmut_10 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_11'] = x_score_benzinga_news__mutmut_11 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_12'] = x_score_benzinga_news__mutmut_12 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_13'] = x_score_benzinga_news__mutmut_13 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_14'] = x_score_benzinga_news__mutmut_14 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_15'] = x_score_benzinga_news__mutmut_15 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_16'] = x_score_benzinga_news__mutmut_16 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_17'] = x_score_benzinga_news__mutmut_17 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_18'] = x_score_benzinga_news__mutmut_18 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_19'] = x_score_benzinga_news__mutmut_19 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_20'] = x_score_benzinga_news__mutmut_20 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_21'] = x_score_benzinga_news__mutmut_21 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_22'] = x_score_benzinga_news__mutmut_22 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_23'] = x_score_benzinga_news__mutmut_23 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_24'] = x_score_benzinga_news__mutmut_24 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_25'] = x_score_benzinga_news__mutmut_25 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_26'] = x_score_benzinga_news__mutmut_26 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_27'] = x_score_benzinga_news__mutmut_27 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_28'] = x_score_benzinga_news__mutmut_28 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_29'] = x_score_benzinga_news__mutmut_29 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_30'] = x_score_benzinga_news__mutmut_30 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_31'] = x_score_benzinga_news__mutmut_31 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_32'] = x_score_benzinga_news__mutmut_32 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_33'] = x_score_benzinga_news__mutmut_33 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_34'] = x_score_benzinga_news__mutmut_34 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_35'] = x_score_benzinga_news__mutmut_35 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_36'] = x_score_benzinga_news__mutmut_36 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_37'] = x_score_benzinga_news__mutmut_37 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_38'] = x_score_benzinga_news__mutmut_38 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_39'] = x_score_benzinga_news__mutmut_39 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_40'] = x_score_benzinga_news__mutmut_40 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_41'] = x_score_benzinga_news__mutmut_41 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_42'] = x_score_benzinga_news__mutmut_42 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_43'] = x_score_benzinga_news__mutmut_43 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_44'] = x_score_benzinga_news__mutmut_44 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_45'] = x_score_benzinga_news__mutmut_45 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_46'] = x_score_benzinga_news__mutmut_46 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_47'] = x_score_benzinga_news__mutmut_47 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_48'] = x_score_benzinga_news__mutmut_48 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_49'] = x_score_benzinga_news__mutmut_49 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_50'] = x_score_benzinga_news__mutmut_50 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_51'] = x_score_benzinga_news__mutmut_51 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_52'] = x_score_benzinga_news__mutmut_52 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_53'] = x_score_benzinga_news__mutmut_53 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_54'] = x_score_benzinga_news__mutmut_54 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_55'] = x_score_benzinga_news__mutmut_55 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_56'] = x_score_benzinga_news__mutmut_56 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_57'] = x_score_benzinga_news__mutmut_57 # type: ignore # mutmut generated
mutants_x_score_benzinga_news__mutmut['x_score_benzinga_news__mutmut_58'] = x_score_benzinga_news__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_benzinga_news_score__mutmut)
async def get_benzinga_news_score(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_orig(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_1(ticker: str) -> dict:
    articles = None
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_2(ticker: str) -> dict:
    articles = await get_benzinga_news(None)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_3(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = None
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_4(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(None)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_5(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"XXscoreXX": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_6(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"SCORE": score, "headline": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_7(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "XXheadlineXX": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_8(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "HEADLINE": headline, "label": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_9(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "XXlabelXX": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_10(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "LABEL": label, "articles": articles[:5]}


async def x_get_benzinga_news_score__mutmut_11(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "XXarticlesXX": articles[:5]}


async def x_get_benzinga_news_score__mutmut_12(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "ARTICLES": articles[:5]}


async def x_get_benzinga_news_score__mutmut_13(ticker: str) -> dict:
    articles = await get_benzinga_news(ticker)
    score, headline, label = score_benzinga_news(articles)
    return {"score": score, "headline": headline, "label": label, "articles": articles[:6]}

mutants_x_get_benzinga_news_score__mutmut['_mutmut_orig'] = x_get_benzinga_news_score__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_1'] = x_get_benzinga_news_score__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_2'] = x_get_benzinga_news_score__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_3'] = x_get_benzinga_news_score__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_4'] = x_get_benzinga_news_score__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_5'] = x_get_benzinga_news_score__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_6'] = x_get_benzinga_news_score__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_7'] = x_get_benzinga_news_score__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_8'] = x_get_benzinga_news_score__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_9'] = x_get_benzinga_news_score__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_10'] = x_get_benzinga_news_score__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_11'] = x_get_benzinga_news_score__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_12'] = x_get_benzinga_news_score__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_benzinga_news_score__mutmut['x_get_benzinga_news_score__mutmut_13'] = x_get_benzinga_news_score__mutmut_13 # type: ignore # mutmut generated


# ── Batch news fetch — 154 tickers in 1-2 paginated API calls ──────────────
# v2/reference/news without ticker filter returns latest 50 articles across ALL tickers.
# Indexing by `tickers` array covers ~20-30 watchlist tickers per page.
# Replaces 154 individual calls (~35s) with 2-3 paginated calls (~5s).

_batch_cache: dict = {"data": {}, "ts": 0.0}
_BATCH_TTL = 600  # 10 minutes
mutants_x_prefetch_news_batch__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_prefetch_news_batch__mutmut)
async def prefetch_news_batch(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_orig(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_1(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = None
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_2(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now + _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_3(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["XXtsXX"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_4(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["TS"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_5(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] <= _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_6(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = None
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_7(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") and ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_8(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") and os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_9(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv(None) or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_10(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("XXMASSIVE_API_KEYXX") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_11(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("massive_api_key") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_12(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv(None) or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_13(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("XXPOLYGON_API_KEYXX") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_14(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("polygon_api_key") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_15(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or "XXXX"
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_16(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_17(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = None
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_18(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(None)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_19(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.lower() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_20(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = None
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_21(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = None
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_22(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = ""

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_23(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(None):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_24(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(4):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_25(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = None
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_26(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "XXlimitXX": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_27(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "LIMIT": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_28(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 51,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_29(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "XXorderXX": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_30(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "ORDER": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_31(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "XXdescXX",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_32(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "DESC",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_33(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "XXsortXX": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_34(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "SORT": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_35(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "XXpublished_utcXX",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_36(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "PUBLISHED_UTC",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_37(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "XXapiKeyXX": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_38(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apikey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_39(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "APIKEY": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_40(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = None
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_41(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["XXcursorXX"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_42(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["CURSOR"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_43(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    None, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_44(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=None, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_45(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=None, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_46(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=None
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_47(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_48(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_49(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_50(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_51(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=None)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_52(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=11)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_53(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_54(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 201:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_55(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_56(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = None
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_57(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = None
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_58(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") and []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_59(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get(None) or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_60(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("XXresultsXX") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_61(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("RESULTS") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_62(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_63(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] and None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_64(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split(None)[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_65(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") and "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_66(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get(None) or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_67(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("XXnext_urlXX") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_68(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("NEXT_URL") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_69(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "XXXX").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_70(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("XXcursor=XX")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_71(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("CURSOR=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_72(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[+1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_73(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-2] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_74(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = None
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_75(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.lower() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_76(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") and [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_77(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get(None) or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_78(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("XXtickersXX") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_79(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("TICKERS") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_80(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = None
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_81(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t not in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_82(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_83(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            break
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_84(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = None
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_85(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get(None, "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_86(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", None)
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_87(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_88(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", )
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_89(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("XXpublished_utcXX", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_90(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("PUBLISHED_UTC", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_91(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "XXXX")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_92(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = None
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_93(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(None, a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_94(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), None)
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_95(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_96(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), )
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_97(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get(None, ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_98(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", None), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_99(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get(""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_100(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_101(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("XXtitleXX", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_102(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("TITLE", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_103(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", "XXXX"), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_104(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get(None, ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_105(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", None))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_106(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get(""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_107(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_108(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("XXdescriptionXX", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_109(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("DESCRIPTION", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_110(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", "XXXX"))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_111(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = None
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_112(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(None)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_113(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = None
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_114(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "XXheadlineXX": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_115(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "HEADLINE": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_116(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get(None, ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_117(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", None),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_118(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get(""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_119(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_120(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("XXtitleXX", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_121(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("TITLE", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_122(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", "XXXX"),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_123(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "XXsentimentXX": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_124(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "SENTIMENT": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_125(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(None, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_126(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, None),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_127(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_128(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, ),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_129(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent / dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_130(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 4),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_131(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "XXraw_sentimentXX": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_132(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "RAW_SENTIMENT": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_133(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(None, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_134(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, None),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_135(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_136(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, ),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_137(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 4),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_138(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "XXurlXX": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_139(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "URL": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_140(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get(None, ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_141(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", None),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_142(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get(""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_143(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_144(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("XXarticle_urlXX", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_145(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("ARTICLE_URL", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_146(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", "XXXX"),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_147(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "XXpublished_atXX": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_148(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "PUBLISHED_AT": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_149(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "XXsourceXX": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_150(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "SOURCE": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_151(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get(None, "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_152(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", None),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_153(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_154(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", ),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_155(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") and {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_156(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get(None) or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_157(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("XXpublisherXX") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_158(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("PUBLISHER") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_159(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("XXnameXX", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_160(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("NAME", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_161(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "XXNewsXX"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_162(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "news"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_163(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "NEWS"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_164(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "XXage_decayXX": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_165(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "AGE_DECAY": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_166(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(None, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_167(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, None),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_168(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_169(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, ),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_170(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 3),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_171(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(None)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_172(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(None, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_173(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, None).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_174(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault([]).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_175(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, ).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_176(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_177(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        return
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_178(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(None)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_179(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(1.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_180(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(None)
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_181(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = None

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_182(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"XXarticlesXX": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_183(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"ARTICLES": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_184(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:11], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_185(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "XXtsXX": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_186(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "TS": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_187(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = None
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_188(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["XXdataXX"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_189(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["DATA"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_190(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = None
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_191(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["XXtsXX"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_192(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["TS"] = now
    log.info(f"[polygon_news] batch: populated cache for {len(ticker_articles)} tickers in 3 API calls (was 154)")


async def x_prefetch_news_batch__mutmut_193(watchlist: list[str]) -> None:
    """
    Fetch the latest global news from Polygon in 3 paginated calls,
    populate the per-ticker _cache so individual get_benzinga_news(ticker)
    calls hit cache instead of making live requests.
    """
    now = time.time()
    if now - _batch_cache["ts"] < _BATCH_TTL:
        return  # already fresh

    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or ""
    if not api_key:
        return

    watchlist_set = set(t.upper() for t in watchlist)
    ssl_ctx = get_ssl_context()
    ticker_articles: dict[str, list] = {}
    cursor = None

    try:
        async with shared_session() as session:
            for _page in range(3):  # 3 pages × 50 articles = 150 most recent
                params: dict = {
                    "limit": 50,
                    "order": "desc",
                    "sort": "published_utc",
                    "apiKey": api_key,
                }
                if cursor:
                    params["cursor"] = cursor
                async with session.get(
                    _BASE, params=params, ssl=ssl_ctx, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    raw = data.get("results") or []
                    cursor = (data.get("next_url") or "").split("cursor=")[-1] or None
                    for a in raw:
                        tickers_in_article = [t.upper() for t in (a.get("tickers") or [])]
                        matched = [t for t in tickers_in_article if t in watchlist_set]
                        if not matched:
                            continue
                        pub = a.get("published_utc", "")
                        sent = _score_headline(a.get("title", ""), a.get("description", ""))
                        dec = _age_decay(pub)
                        art = {
                            "headline": a.get("title", ""),
                            "sentiment": round(sent * dec, 3),
                            "raw_sentiment": round(sent, 3),
                            "url": a.get("article_url", ""),
                            "published_at": pub,
                            "source": (a.get("publisher") or {}).get("name", "News"),
                            "age_decay": round(dec, 2),
                        }
                        for t in matched:
                            ticker_articles.setdefault(t, []).append(art)
                    if not cursor:
                        break
                await asyncio.sleep(0.2)  # rate limit buffer
    except Exception as e:
        log.debug(f"[polygon_news] batch fetch error: {e}")
        return

    # Populate per-ticker cache so individual callers skip the network
    for ticker, articles in ticker_articles.items():
        _cache[ticker] = {"articles": articles[:10], "ts": now}

    _batch_cache["data"] = ticker_articles
    _batch_cache["ts"] = now
    log.info(None)

mutants_x_prefetch_news_batch__mutmut['_mutmut_orig'] = x_prefetch_news_batch__mutmut_orig # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_1'] = x_prefetch_news_batch__mutmut_1 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_2'] = x_prefetch_news_batch__mutmut_2 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_3'] = x_prefetch_news_batch__mutmut_3 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_4'] = x_prefetch_news_batch__mutmut_4 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_5'] = x_prefetch_news_batch__mutmut_5 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_6'] = x_prefetch_news_batch__mutmut_6 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_7'] = x_prefetch_news_batch__mutmut_7 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_8'] = x_prefetch_news_batch__mutmut_8 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_9'] = x_prefetch_news_batch__mutmut_9 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_10'] = x_prefetch_news_batch__mutmut_10 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_11'] = x_prefetch_news_batch__mutmut_11 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_12'] = x_prefetch_news_batch__mutmut_12 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_13'] = x_prefetch_news_batch__mutmut_13 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_14'] = x_prefetch_news_batch__mutmut_14 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_15'] = x_prefetch_news_batch__mutmut_15 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_16'] = x_prefetch_news_batch__mutmut_16 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_17'] = x_prefetch_news_batch__mutmut_17 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_18'] = x_prefetch_news_batch__mutmut_18 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_19'] = x_prefetch_news_batch__mutmut_19 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_20'] = x_prefetch_news_batch__mutmut_20 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_21'] = x_prefetch_news_batch__mutmut_21 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_22'] = x_prefetch_news_batch__mutmut_22 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_23'] = x_prefetch_news_batch__mutmut_23 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_24'] = x_prefetch_news_batch__mutmut_24 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_25'] = x_prefetch_news_batch__mutmut_25 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_26'] = x_prefetch_news_batch__mutmut_26 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_27'] = x_prefetch_news_batch__mutmut_27 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_28'] = x_prefetch_news_batch__mutmut_28 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_29'] = x_prefetch_news_batch__mutmut_29 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_30'] = x_prefetch_news_batch__mutmut_30 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_31'] = x_prefetch_news_batch__mutmut_31 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_32'] = x_prefetch_news_batch__mutmut_32 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_33'] = x_prefetch_news_batch__mutmut_33 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_34'] = x_prefetch_news_batch__mutmut_34 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_35'] = x_prefetch_news_batch__mutmut_35 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_36'] = x_prefetch_news_batch__mutmut_36 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_37'] = x_prefetch_news_batch__mutmut_37 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_38'] = x_prefetch_news_batch__mutmut_38 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_39'] = x_prefetch_news_batch__mutmut_39 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_40'] = x_prefetch_news_batch__mutmut_40 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_41'] = x_prefetch_news_batch__mutmut_41 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_42'] = x_prefetch_news_batch__mutmut_42 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_43'] = x_prefetch_news_batch__mutmut_43 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_44'] = x_prefetch_news_batch__mutmut_44 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_45'] = x_prefetch_news_batch__mutmut_45 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_46'] = x_prefetch_news_batch__mutmut_46 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_47'] = x_prefetch_news_batch__mutmut_47 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_48'] = x_prefetch_news_batch__mutmut_48 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_49'] = x_prefetch_news_batch__mutmut_49 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_50'] = x_prefetch_news_batch__mutmut_50 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_51'] = x_prefetch_news_batch__mutmut_51 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_52'] = x_prefetch_news_batch__mutmut_52 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_53'] = x_prefetch_news_batch__mutmut_53 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_54'] = x_prefetch_news_batch__mutmut_54 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_55'] = x_prefetch_news_batch__mutmut_55 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_56'] = x_prefetch_news_batch__mutmut_56 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_57'] = x_prefetch_news_batch__mutmut_57 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_58'] = x_prefetch_news_batch__mutmut_58 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_59'] = x_prefetch_news_batch__mutmut_59 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_60'] = x_prefetch_news_batch__mutmut_60 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_61'] = x_prefetch_news_batch__mutmut_61 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_62'] = x_prefetch_news_batch__mutmut_62 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_63'] = x_prefetch_news_batch__mutmut_63 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_64'] = x_prefetch_news_batch__mutmut_64 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_65'] = x_prefetch_news_batch__mutmut_65 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_66'] = x_prefetch_news_batch__mutmut_66 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_67'] = x_prefetch_news_batch__mutmut_67 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_68'] = x_prefetch_news_batch__mutmut_68 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_69'] = x_prefetch_news_batch__mutmut_69 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_70'] = x_prefetch_news_batch__mutmut_70 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_71'] = x_prefetch_news_batch__mutmut_71 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_72'] = x_prefetch_news_batch__mutmut_72 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_73'] = x_prefetch_news_batch__mutmut_73 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_74'] = x_prefetch_news_batch__mutmut_74 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_75'] = x_prefetch_news_batch__mutmut_75 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_76'] = x_prefetch_news_batch__mutmut_76 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_77'] = x_prefetch_news_batch__mutmut_77 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_78'] = x_prefetch_news_batch__mutmut_78 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_79'] = x_prefetch_news_batch__mutmut_79 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_80'] = x_prefetch_news_batch__mutmut_80 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_81'] = x_prefetch_news_batch__mutmut_81 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_82'] = x_prefetch_news_batch__mutmut_82 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_83'] = x_prefetch_news_batch__mutmut_83 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_84'] = x_prefetch_news_batch__mutmut_84 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_85'] = x_prefetch_news_batch__mutmut_85 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_86'] = x_prefetch_news_batch__mutmut_86 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_87'] = x_prefetch_news_batch__mutmut_87 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_88'] = x_prefetch_news_batch__mutmut_88 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_89'] = x_prefetch_news_batch__mutmut_89 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_90'] = x_prefetch_news_batch__mutmut_90 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_91'] = x_prefetch_news_batch__mutmut_91 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_92'] = x_prefetch_news_batch__mutmut_92 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_93'] = x_prefetch_news_batch__mutmut_93 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_94'] = x_prefetch_news_batch__mutmut_94 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_95'] = x_prefetch_news_batch__mutmut_95 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_96'] = x_prefetch_news_batch__mutmut_96 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_97'] = x_prefetch_news_batch__mutmut_97 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_98'] = x_prefetch_news_batch__mutmut_98 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_99'] = x_prefetch_news_batch__mutmut_99 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_100'] = x_prefetch_news_batch__mutmut_100 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_101'] = x_prefetch_news_batch__mutmut_101 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_102'] = x_prefetch_news_batch__mutmut_102 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_103'] = x_prefetch_news_batch__mutmut_103 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_104'] = x_prefetch_news_batch__mutmut_104 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_105'] = x_prefetch_news_batch__mutmut_105 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_106'] = x_prefetch_news_batch__mutmut_106 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_107'] = x_prefetch_news_batch__mutmut_107 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_108'] = x_prefetch_news_batch__mutmut_108 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_109'] = x_prefetch_news_batch__mutmut_109 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_110'] = x_prefetch_news_batch__mutmut_110 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_111'] = x_prefetch_news_batch__mutmut_111 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_112'] = x_prefetch_news_batch__mutmut_112 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_113'] = x_prefetch_news_batch__mutmut_113 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_114'] = x_prefetch_news_batch__mutmut_114 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_115'] = x_prefetch_news_batch__mutmut_115 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_116'] = x_prefetch_news_batch__mutmut_116 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_117'] = x_prefetch_news_batch__mutmut_117 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_118'] = x_prefetch_news_batch__mutmut_118 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_119'] = x_prefetch_news_batch__mutmut_119 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_120'] = x_prefetch_news_batch__mutmut_120 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_121'] = x_prefetch_news_batch__mutmut_121 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_122'] = x_prefetch_news_batch__mutmut_122 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_123'] = x_prefetch_news_batch__mutmut_123 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_124'] = x_prefetch_news_batch__mutmut_124 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_125'] = x_prefetch_news_batch__mutmut_125 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_126'] = x_prefetch_news_batch__mutmut_126 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_127'] = x_prefetch_news_batch__mutmut_127 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_128'] = x_prefetch_news_batch__mutmut_128 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_129'] = x_prefetch_news_batch__mutmut_129 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_130'] = x_prefetch_news_batch__mutmut_130 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_131'] = x_prefetch_news_batch__mutmut_131 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_132'] = x_prefetch_news_batch__mutmut_132 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_133'] = x_prefetch_news_batch__mutmut_133 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_134'] = x_prefetch_news_batch__mutmut_134 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_135'] = x_prefetch_news_batch__mutmut_135 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_136'] = x_prefetch_news_batch__mutmut_136 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_137'] = x_prefetch_news_batch__mutmut_137 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_138'] = x_prefetch_news_batch__mutmut_138 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_139'] = x_prefetch_news_batch__mutmut_139 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_140'] = x_prefetch_news_batch__mutmut_140 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_141'] = x_prefetch_news_batch__mutmut_141 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_142'] = x_prefetch_news_batch__mutmut_142 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_143'] = x_prefetch_news_batch__mutmut_143 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_144'] = x_prefetch_news_batch__mutmut_144 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_145'] = x_prefetch_news_batch__mutmut_145 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_146'] = x_prefetch_news_batch__mutmut_146 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_147'] = x_prefetch_news_batch__mutmut_147 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_148'] = x_prefetch_news_batch__mutmut_148 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_149'] = x_prefetch_news_batch__mutmut_149 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_150'] = x_prefetch_news_batch__mutmut_150 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_151'] = x_prefetch_news_batch__mutmut_151 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_152'] = x_prefetch_news_batch__mutmut_152 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_153'] = x_prefetch_news_batch__mutmut_153 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_154'] = x_prefetch_news_batch__mutmut_154 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_155'] = x_prefetch_news_batch__mutmut_155 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_156'] = x_prefetch_news_batch__mutmut_156 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_157'] = x_prefetch_news_batch__mutmut_157 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_158'] = x_prefetch_news_batch__mutmut_158 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_159'] = x_prefetch_news_batch__mutmut_159 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_160'] = x_prefetch_news_batch__mutmut_160 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_161'] = x_prefetch_news_batch__mutmut_161 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_162'] = x_prefetch_news_batch__mutmut_162 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_163'] = x_prefetch_news_batch__mutmut_163 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_164'] = x_prefetch_news_batch__mutmut_164 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_165'] = x_prefetch_news_batch__mutmut_165 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_166'] = x_prefetch_news_batch__mutmut_166 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_167'] = x_prefetch_news_batch__mutmut_167 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_168'] = x_prefetch_news_batch__mutmut_168 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_169'] = x_prefetch_news_batch__mutmut_169 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_170'] = x_prefetch_news_batch__mutmut_170 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_171'] = x_prefetch_news_batch__mutmut_171 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_172'] = x_prefetch_news_batch__mutmut_172 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_173'] = x_prefetch_news_batch__mutmut_173 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_174'] = x_prefetch_news_batch__mutmut_174 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_175'] = x_prefetch_news_batch__mutmut_175 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_176'] = x_prefetch_news_batch__mutmut_176 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_177'] = x_prefetch_news_batch__mutmut_177 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_178'] = x_prefetch_news_batch__mutmut_178 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_179'] = x_prefetch_news_batch__mutmut_179 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_180'] = x_prefetch_news_batch__mutmut_180 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_181'] = x_prefetch_news_batch__mutmut_181 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_182'] = x_prefetch_news_batch__mutmut_182 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_183'] = x_prefetch_news_batch__mutmut_183 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_184'] = x_prefetch_news_batch__mutmut_184 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_185'] = x_prefetch_news_batch__mutmut_185 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_186'] = x_prefetch_news_batch__mutmut_186 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_187'] = x_prefetch_news_batch__mutmut_187 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_188'] = x_prefetch_news_batch__mutmut_188 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_189'] = x_prefetch_news_batch__mutmut_189 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_190'] = x_prefetch_news_batch__mutmut_190 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_191'] = x_prefetch_news_batch__mutmut_191 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_192'] = x_prefetch_news_batch__mutmut_192 # type: ignore # mutmut generated
mutants_x_prefetch_news_batch__mutmut['x_prefetch_news_batch__mutmut_193'] = x_prefetch_news_batch__mutmut_193 # type: ignore # mutmut generated
