import logging
import ssl
import time
from typing import Optional

log = logging.getLogger("signal.trade.fear_greed")

import aiohttp
import certifi

from services.redis_cache import cache_get, cache_set
from services.http_client import get_ssl_context, shared_session

_cache: dict = {"data": None, "ts": 0.0}  # in-process fallback for serve-stale-on-error
_ssl_ctx: ssl.SSLContext = ssl.create_default_context(cafile=certifi.where())
CACHE_TTL = 3600  # refresh once per hour
_CACHE_KEY = "fear_greed:data"

URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
_REFERER = "https://www.cnn.com/markets/fear-and-greed"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": _REFERER,
    "Origin": "https://www.cnn.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

# (lo, hi) → (label, sentiment for rationale, confidence_bias)
_BANDS = [
    (0, 25, "Extreme Fear", "pos", +15),  # contrarian: oversold market = buy dip
    (25, 45, "Fear", "pos", +7),
    (45, 55, "Neutral", "neu", 0),
    (55, 75, "Greed", "neg", -5),
    (75, 101, "Extreme Greed", "neg", -13),  # complacency = top risk
]


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__classify__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__classify__mutmut)
def _classify(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "neu", 0


def x__classify__mutmut_orig(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "neu", 0


def x__classify__mutmut_1(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo < score < hi:
            return label, sentiment, bias
    return "Neutral", "neu", 0


def x__classify__mutmut_2(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score <= hi:
            return label, sentiment, bias
    return "Neutral", "neu", 0


def x__classify__mutmut_3(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "XXNeutralXX", "neu", 0


def x__classify__mutmut_4(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "neutral", "neu", 0


def x__classify__mutmut_5(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "NEUTRAL", "neu", 0


def x__classify__mutmut_6(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "XXneuXX", 0


def x__classify__mutmut_7(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "NEU", 0


def x__classify__mutmut_8(score: float) -> tuple[str, str, int]:
    for lo, hi, label, sentiment, bias in _BANDS:
        if lo <= score < hi:
            return label, sentiment, bias
    return "Neutral", "neu", 1

mutants_x__classify__mutmut['_mutmut_orig'] = x__classify__mutmut_orig # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_1'] = x__classify__mutmut_1 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_2'] = x__classify__mutmut_2 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_3'] = x__classify__mutmut_3 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_4'] = x__classify__mutmut_4 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_5'] = x__classify__mutmut_5 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_6'] = x__classify__mutmut_6 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_7'] = x__classify__mutmut_7 # type: ignore # mutmut generated
mutants_x__classify__mutmut['x__classify__mutmut_8'] = x__classify__mutmut_8 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__neutral_result__mutmut)
def _neutral_result() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_orig() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_1() -> dict:
    score = None
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_2() -> dict:
    score = 51.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_3() -> dict:
    score = 50.0
    label, sentiment, bias = None
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_4() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(None)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_5() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "XXscoreXX": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_6() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "SCORE": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_7() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(None, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_8() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, None),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_9() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_10() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, ),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_11() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 2),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_12() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "XXlabelXX": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_13() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "LABEL": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_14() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "XXsentimentXX": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_15() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "SENTIMENT": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_16() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "XXscore_biasXX": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_17() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "SCORE_BIAS": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_18() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "XXprev_closeXX": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_19() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "PREV_CLOSE": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_20() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(None, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_21() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, None),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_22() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_23() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, ),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_24() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 2),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_25() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "XXprev_1wXX": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_26() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "PREV_1W": round(score, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_27() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(None, 1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_28() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, None),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_29() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(1),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_30() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, ),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_31() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 2),
        "prev_1m": round(score, 1),
    }


def x__neutral_result__mutmut_32() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "XXprev_1mXX": round(score, 1),
    }


def x__neutral_result__mutmut_33() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "PREV_1M": round(score, 1),
    }


def x__neutral_result__mutmut_34() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(None, 1),
    }


def x__neutral_result__mutmut_35() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, None),
    }


def x__neutral_result__mutmut_36() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(1),
    }


def x__neutral_result__mutmut_37() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, ),
    }


def x__neutral_result__mutmut_38() -> dict:
    score = 50.0
    label, sentiment, bias = _classify(score)
    return {
        "score": round(score, 1),
        "label": label,
        "sentiment": sentiment,
        "score_bias": bias,
        "prev_close": round(score, 1),
        "prev_1w": round(score, 1),
        "prev_1m": round(score, 2),
    }

mutants_x__neutral_result__mutmut['_mutmut_orig'] = x__neutral_result__mutmut_orig # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_1'] = x__neutral_result__mutmut_1 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_2'] = x__neutral_result__mutmut_2 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_3'] = x__neutral_result__mutmut_3 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_4'] = x__neutral_result__mutmut_4 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_5'] = x__neutral_result__mutmut_5 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_6'] = x__neutral_result__mutmut_6 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_7'] = x__neutral_result__mutmut_7 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_8'] = x__neutral_result__mutmut_8 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_9'] = x__neutral_result__mutmut_9 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_10'] = x__neutral_result__mutmut_10 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_11'] = x__neutral_result__mutmut_11 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_12'] = x__neutral_result__mutmut_12 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_13'] = x__neutral_result__mutmut_13 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_14'] = x__neutral_result__mutmut_14 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_15'] = x__neutral_result__mutmut_15 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_16'] = x__neutral_result__mutmut_16 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_17'] = x__neutral_result__mutmut_17 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_18'] = x__neutral_result__mutmut_18 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_19'] = x__neutral_result__mutmut_19 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_20'] = x__neutral_result__mutmut_20 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_21'] = x__neutral_result__mutmut_21 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_22'] = x__neutral_result__mutmut_22 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_23'] = x__neutral_result__mutmut_23 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_24'] = x__neutral_result__mutmut_24 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_25'] = x__neutral_result__mutmut_25 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_26'] = x__neutral_result__mutmut_26 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_27'] = x__neutral_result__mutmut_27 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_28'] = x__neutral_result__mutmut_28 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_29'] = x__neutral_result__mutmut_29 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_30'] = x__neutral_result__mutmut_30 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_31'] = x__neutral_result__mutmut_31 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_32'] = x__neutral_result__mutmut_32 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_33'] = x__neutral_result__mutmut_33 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_34'] = x__neutral_result__mutmut_34 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_35'] = x__neutral_result__mutmut_35 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_36'] = x__neutral_result__mutmut_36 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_37'] = x__neutral_result__mutmut_37 # type: ignore # mutmut generated
mutants_x__neutral_result__mutmut['x__neutral_result__mutmut_38'] = x__neutral_result__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_fear_greed__mutmut)
async def get_fear_greed() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_orig() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_1() -> Optional[dict]:
    cached = None
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_2() -> Optional[dict]:
    cached = await cache_get(None)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_3() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_4() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None or time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_5() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get(None) is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_6() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("XXdataXX") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_7() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("DATA") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_8() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_9() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() + _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_10() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get(None, 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_11() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", None) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_12() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get(0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_13() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", ) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_14() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("XXtsXX", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_15() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("TS", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_16() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 1.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_17() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) <= CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_18() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["XXdataXX"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_19() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["DATA"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_20() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = None
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_21() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=None)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_22() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=None) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_23() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                None,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_24() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=None,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_25() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=None,
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_26() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_27() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_28() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_29() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=None),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_30() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=11),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_31() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_32() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 201:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_33() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(None)
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_34() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["XXdataXX"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_35() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["DATA"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_36() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get(None) is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_37() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("XXdataXX") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_38() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("DATA") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_39() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_40() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = None

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_41() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = None
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_42() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get(None, raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_43() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", None)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_44() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get(raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_45() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", )
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_46() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("XXfear_and_greedXX", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_47() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("FEAR_AND_GREED", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_48() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = None
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_49() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(None)
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_50() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get(None, fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_51() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", None))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_52() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get(fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_53() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", ))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_54() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("XXscoreXX", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_55() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("SCORE", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_56() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get(None, 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_57() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", None)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_58() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get(50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_59() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", )))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_60() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("XXcurrent_valueXX", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_61() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("CURRENT_VALUE", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_62() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 51)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_63() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = None

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_64() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(None)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_65() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = None
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_66() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "XXscoreXX": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_67() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "SCORE": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_68() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(None, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_69() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, None),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_70() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_71() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, ),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_72() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 2),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_73() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "XXlabelXX": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_74() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "LABEL": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_75() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "XXsentimentXX": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_76() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "SENTIMENT": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_77() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "XXscore_biasXX": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_78() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "SCORE_BIAS": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_79() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "XXprev_closeXX": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_80() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "PREV_CLOSE": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_81() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(None, 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_82() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), None),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_83() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_84() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), ),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_85() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(None), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_86() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get(None, score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_87() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", None)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_88() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get(score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_89() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", )), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_90() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("XXprevious_closeXX", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_91() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("PREVIOUS_CLOSE", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_92() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 2),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_93() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "XXprev_1wXX": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_94() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "PREV_1W": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_95() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(None, 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_96() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), None),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_97() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_98() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), ),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_99() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(None), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_100() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get(None, score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_101() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", None)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_102() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get(score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_103() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", )), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_104() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("XXprevious_1_weekXX", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_105() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("PREVIOUS_1_WEEK", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_106() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 2),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_107() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "XXprev_1mXX": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_108() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "PREV_1M": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_109() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(None, 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_110() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), None),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_111() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_112() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), ),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_113() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(None), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_114() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get(None, score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_115() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", None)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_116() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get(score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_117() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", )), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_118() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("XXprevious_1_monthXX", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_119() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("PREVIOUS_1_MONTH", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_120() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 2),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_121() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = None
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_122() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["XXdataXX"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_123() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["DATA"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_124() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = None
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_125() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["XXtsXX"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_126() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["TS"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_127() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(None, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_128() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, None, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_129() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=None)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_130() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_131() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_132() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, )
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_133() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(None)
        return _cache.get("data") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_134() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get(None) if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_135() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("XXdataXX") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_136() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("DATA") if _cache.get("data") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_137() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get(None) is not None else _neutral_result()


async def x_get_fear_greed__mutmut_138() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("XXdataXX") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_139() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("DATA") is not None else _neutral_result()


async def x_get_fear_greed__mutmut_140() -> Optional[dict]:
    cached = await cache_get(_CACHE_KEY)
    if cached is not None:
        return cached
    # In-process stale fallback while waiting for cache population
    if _cache.get("data") is not None and time.time() - _cache.get("ts", 0.0) < CACHE_TTL:
        return _cache["data"]

    try:
        connector = aiohttp.TCPConnector(ssl=_ssl_ctx)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                URL,
                headers=_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.warning(f"[fear_greed] HTTP {resp.status} from CNN API")
                    return _cache["data"] if _cache.get("data") is not None else _neutral_result()
                raw = await resp.json(content_type=None)

        fg = raw.get("fear_and_greed", raw)
        score = float(fg.get("score", fg.get("current_value", 50)))
        label, sentiment, bias = _classify(score)

        result = {
            "score": round(score, 1),
            "label": label,
            "sentiment": sentiment,
            "score_bias": bias,
            "prev_close": round(float(fg.get("previous_close", score)), 1),
            "prev_1w": round(float(fg.get("previous_1_week", score)), 1),
            "prev_1m": round(float(fg.get("previous_1_month", score)), 1),
        }
        _cache["data"] = result
        _cache["ts"] = time.time()
        await cache_set(_CACHE_KEY, result, ttl=CACHE_TTL)
        return result

    except Exception as e:
        log.warning(f"[fear_greed] {e}")
        return _cache.get("data") if _cache.get("data") is None else _neutral_result()

mutants_x_get_fear_greed__mutmut['_mutmut_orig'] = x_get_fear_greed__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_1'] = x_get_fear_greed__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_2'] = x_get_fear_greed__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_3'] = x_get_fear_greed__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_4'] = x_get_fear_greed__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_5'] = x_get_fear_greed__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_6'] = x_get_fear_greed__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_7'] = x_get_fear_greed__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_8'] = x_get_fear_greed__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_9'] = x_get_fear_greed__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_10'] = x_get_fear_greed__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_11'] = x_get_fear_greed__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_12'] = x_get_fear_greed__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_13'] = x_get_fear_greed__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_14'] = x_get_fear_greed__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_15'] = x_get_fear_greed__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_16'] = x_get_fear_greed__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_17'] = x_get_fear_greed__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_18'] = x_get_fear_greed__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_19'] = x_get_fear_greed__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_20'] = x_get_fear_greed__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_21'] = x_get_fear_greed__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_22'] = x_get_fear_greed__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_23'] = x_get_fear_greed__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_24'] = x_get_fear_greed__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_25'] = x_get_fear_greed__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_26'] = x_get_fear_greed__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_27'] = x_get_fear_greed__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_28'] = x_get_fear_greed__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_29'] = x_get_fear_greed__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_30'] = x_get_fear_greed__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_31'] = x_get_fear_greed__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_32'] = x_get_fear_greed__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_33'] = x_get_fear_greed__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_34'] = x_get_fear_greed__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_35'] = x_get_fear_greed__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_36'] = x_get_fear_greed__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_37'] = x_get_fear_greed__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_38'] = x_get_fear_greed__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_39'] = x_get_fear_greed__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_40'] = x_get_fear_greed__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_41'] = x_get_fear_greed__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_42'] = x_get_fear_greed__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_43'] = x_get_fear_greed__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_44'] = x_get_fear_greed__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_45'] = x_get_fear_greed__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_46'] = x_get_fear_greed__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_47'] = x_get_fear_greed__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_48'] = x_get_fear_greed__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_49'] = x_get_fear_greed__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_50'] = x_get_fear_greed__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_51'] = x_get_fear_greed__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_52'] = x_get_fear_greed__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_53'] = x_get_fear_greed__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_54'] = x_get_fear_greed__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_55'] = x_get_fear_greed__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_56'] = x_get_fear_greed__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_57'] = x_get_fear_greed__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_58'] = x_get_fear_greed__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_59'] = x_get_fear_greed__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_60'] = x_get_fear_greed__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_61'] = x_get_fear_greed__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_62'] = x_get_fear_greed__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_63'] = x_get_fear_greed__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_64'] = x_get_fear_greed__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_65'] = x_get_fear_greed__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_66'] = x_get_fear_greed__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_67'] = x_get_fear_greed__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_68'] = x_get_fear_greed__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_69'] = x_get_fear_greed__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_70'] = x_get_fear_greed__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_71'] = x_get_fear_greed__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_72'] = x_get_fear_greed__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_73'] = x_get_fear_greed__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_74'] = x_get_fear_greed__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_75'] = x_get_fear_greed__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_76'] = x_get_fear_greed__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_77'] = x_get_fear_greed__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_78'] = x_get_fear_greed__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_79'] = x_get_fear_greed__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_80'] = x_get_fear_greed__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_81'] = x_get_fear_greed__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_82'] = x_get_fear_greed__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_83'] = x_get_fear_greed__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_84'] = x_get_fear_greed__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_85'] = x_get_fear_greed__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_86'] = x_get_fear_greed__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_87'] = x_get_fear_greed__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_88'] = x_get_fear_greed__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_89'] = x_get_fear_greed__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_90'] = x_get_fear_greed__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_91'] = x_get_fear_greed__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_92'] = x_get_fear_greed__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_93'] = x_get_fear_greed__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_94'] = x_get_fear_greed__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_95'] = x_get_fear_greed__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_96'] = x_get_fear_greed__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_97'] = x_get_fear_greed__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_98'] = x_get_fear_greed__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_99'] = x_get_fear_greed__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_100'] = x_get_fear_greed__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_101'] = x_get_fear_greed__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_102'] = x_get_fear_greed__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_103'] = x_get_fear_greed__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_104'] = x_get_fear_greed__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_105'] = x_get_fear_greed__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_106'] = x_get_fear_greed__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_107'] = x_get_fear_greed__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_108'] = x_get_fear_greed__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_109'] = x_get_fear_greed__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_110'] = x_get_fear_greed__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_111'] = x_get_fear_greed__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_112'] = x_get_fear_greed__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_113'] = x_get_fear_greed__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_114'] = x_get_fear_greed__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_115'] = x_get_fear_greed__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_116'] = x_get_fear_greed__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_117'] = x_get_fear_greed__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_118'] = x_get_fear_greed__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_119'] = x_get_fear_greed__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_120'] = x_get_fear_greed__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_121'] = x_get_fear_greed__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_122'] = x_get_fear_greed__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_123'] = x_get_fear_greed__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_124'] = x_get_fear_greed__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_125'] = x_get_fear_greed__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_126'] = x_get_fear_greed__mutmut_126 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_127'] = x_get_fear_greed__mutmut_127 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_128'] = x_get_fear_greed__mutmut_128 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_129'] = x_get_fear_greed__mutmut_129 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_130'] = x_get_fear_greed__mutmut_130 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_131'] = x_get_fear_greed__mutmut_131 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_132'] = x_get_fear_greed__mutmut_132 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_133'] = x_get_fear_greed__mutmut_133 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_134'] = x_get_fear_greed__mutmut_134 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_135'] = x_get_fear_greed__mutmut_135 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_136'] = x_get_fear_greed__mutmut_136 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_137'] = x_get_fear_greed__mutmut_137 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_138'] = x_get_fear_greed__mutmut_138 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_139'] = x_get_fear_greed__mutmut_139 # type: ignore # mutmut generated
mutants_x_get_fear_greed__mutmut['x_get_fear_greed__mutmut_140'] = x_get_fear_greed__mutmut_140 # type: ignore # mutmut generated


import csv
import io as _io

_pc_cache: dict = {"ratio": None, "ts": 0.0}
mutants_x_get_put_call_ratio__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_put_call_ratio__mutmut)
async def get_put_call_ratio() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_orig() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_1() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = None
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_2() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None or now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_3() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["XXratioXX"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_4() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["RATIO"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_5() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_6() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now + _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_7() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["XXtsXX"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_8() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["TS"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_9() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] <= 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_10() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 / 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_11() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3601 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_12() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 5:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_13() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["XXratioXX"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_14() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["RATIO"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_15() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = None
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_16() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = None
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_17() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "XXhttps://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csvXX"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_18() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "HTTPS://WWW.CBOE.COM/PUBLISH/SCHEDULEDTASK/MKTDATA/TODAYS_OPTIONS_STATISTICS.CSV"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_19() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(None, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_20() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=None, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_21() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=None) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_22() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_23() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_24() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, ) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_25() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=None)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_26() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=11)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_27() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_28() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 201:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_29() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = None
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_30() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = None
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_31() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(None)
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_32() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(None))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_33() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = None
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_34() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_35() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                break
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_36() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = None
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_37() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_38() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = None
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_39() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.upper() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_40() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                break
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_41() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) <= len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_42() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                break
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_43() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = None
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_44() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(None)
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_45() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(None, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_46() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, None))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_47() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_48() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, ))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_49() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = None
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_50() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") and d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_51() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get(None) or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_52() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("XXtotal put/call ratioXX") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_53() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("TOTAL PUT/CALL RATIO") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_54() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get(None)
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_55() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("XXtotal p/c ratioXX")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_56() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("TOTAL P/C RATIO")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_57() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = None
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_58() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(None)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_59() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = None
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_60() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "XXratioXX": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_61() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "RATIO": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_62() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(None, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_63() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, None),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_64() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_65() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, ),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_66() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 4),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_67() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "XXsignalXX": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_68() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "SIGNAL": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_69() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "XXbullishXX" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_70() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "BULLISH" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_71() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio >= 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_72() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 2.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_73() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "XXbearishXX" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_74() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "BEARISH" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_75() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio <= 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_76() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 1.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_77() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "XXneutralXX",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_78() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "NEUTRAL",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_79() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "XXbiasXX": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_80() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "BIAS": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_81() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 11 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_82() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio >= 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_83() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 2.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_84() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else +10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_85() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -11 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_86() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio <= 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_87() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 1.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_88() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 1,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_89() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = None
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_90() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["XXratioXX"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_91() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["RATIO"] = result
                    _pc_cache["ts"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_92() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["ts"] = None
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_93() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["XXtsXX"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None


async def x_get_put_call_ratio__mutmut_94() -> dict | None:
    """CBOE total put/call ratio — free daily CSV, no key needed."""
    import time

    import aiohttp

    now = time.time()
    if _pc_cache["ratio"] is not None and now - _pc_cache["ts"] < 3600 * 4:
        return _pc_cache["ratio"]
    ctx = get_ssl_context()
    url = "https://www.cboe.com/publish/scheduledtask/mktdata/todays_options_statistics.csv"
    try:
        async with shared_session() as s:
            async with s.get(url, ssl=ctx, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return None
                text = await r.text()
        reader = csv.reader(_io.StringIO(text))
        headers = []
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            if not headers:
                headers = [h.lower() for h in row]
                continue
            if len(row) < len(headers):
                continue
            d = dict(zip(headers, row))
            total = d.get("total put/call ratio") or d.get("total p/c ratio")
            if total:
                try:
                    ratio = float(total)
                    result = {
                        "ratio": round(ratio, 3),
                        "signal": "bullish" if ratio > 1.15 else "bearish" if ratio < 0.65 else "neutral",
                        "bias": 10 if ratio > 1.15 else -10 if ratio < 0.65 else 0,
                    }
                    _pc_cache["ratio"] = result
                    _pc_cache["TS"] = now
                    return result
                except ValueError:
                    pass
    except Exception:
        pass
    return None

mutants_x_get_put_call_ratio__mutmut['_mutmut_orig'] = x_get_put_call_ratio__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_1'] = x_get_put_call_ratio__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_2'] = x_get_put_call_ratio__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_3'] = x_get_put_call_ratio__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_4'] = x_get_put_call_ratio__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_5'] = x_get_put_call_ratio__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_6'] = x_get_put_call_ratio__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_7'] = x_get_put_call_ratio__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_8'] = x_get_put_call_ratio__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_9'] = x_get_put_call_ratio__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_10'] = x_get_put_call_ratio__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_11'] = x_get_put_call_ratio__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_12'] = x_get_put_call_ratio__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_13'] = x_get_put_call_ratio__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_14'] = x_get_put_call_ratio__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_15'] = x_get_put_call_ratio__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_16'] = x_get_put_call_ratio__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_17'] = x_get_put_call_ratio__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_18'] = x_get_put_call_ratio__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_19'] = x_get_put_call_ratio__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_20'] = x_get_put_call_ratio__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_21'] = x_get_put_call_ratio__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_22'] = x_get_put_call_ratio__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_23'] = x_get_put_call_ratio__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_24'] = x_get_put_call_ratio__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_25'] = x_get_put_call_ratio__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_26'] = x_get_put_call_ratio__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_27'] = x_get_put_call_ratio__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_28'] = x_get_put_call_ratio__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_29'] = x_get_put_call_ratio__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_30'] = x_get_put_call_ratio__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_31'] = x_get_put_call_ratio__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_32'] = x_get_put_call_ratio__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_33'] = x_get_put_call_ratio__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_34'] = x_get_put_call_ratio__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_35'] = x_get_put_call_ratio__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_36'] = x_get_put_call_ratio__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_37'] = x_get_put_call_ratio__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_38'] = x_get_put_call_ratio__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_39'] = x_get_put_call_ratio__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_40'] = x_get_put_call_ratio__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_41'] = x_get_put_call_ratio__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_42'] = x_get_put_call_ratio__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_43'] = x_get_put_call_ratio__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_44'] = x_get_put_call_ratio__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_45'] = x_get_put_call_ratio__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_46'] = x_get_put_call_ratio__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_47'] = x_get_put_call_ratio__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_48'] = x_get_put_call_ratio__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_49'] = x_get_put_call_ratio__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_50'] = x_get_put_call_ratio__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_51'] = x_get_put_call_ratio__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_52'] = x_get_put_call_ratio__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_53'] = x_get_put_call_ratio__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_54'] = x_get_put_call_ratio__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_55'] = x_get_put_call_ratio__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_56'] = x_get_put_call_ratio__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_57'] = x_get_put_call_ratio__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_58'] = x_get_put_call_ratio__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_59'] = x_get_put_call_ratio__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_60'] = x_get_put_call_ratio__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_61'] = x_get_put_call_ratio__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_62'] = x_get_put_call_ratio__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_63'] = x_get_put_call_ratio__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_64'] = x_get_put_call_ratio__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_65'] = x_get_put_call_ratio__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_66'] = x_get_put_call_ratio__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_67'] = x_get_put_call_ratio__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_68'] = x_get_put_call_ratio__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_69'] = x_get_put_call_ratio__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_70'] = x_get_put_call_ratio__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_71'] = x_get_put_call_ratio__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_72'] = x_get_put_call_ratio__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_73'] = x_get_put_call_ratio__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_74'] = x_get_put_call_ratio__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_75'] = x_get_put_call_ratio__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_76'] = x_get_put_call_ratio__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_77'] = x_get_put_call_ratio__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_78'] = x_get_put_call_ratio__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_79'] = x_get_put_call_ratio__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_80'] = x_get_put_call_ratio__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_81'] = x_get_put_call_ratio__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_82'] = x_get_put_call_ratio__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_83'] = x_get_put_call_ratio__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_84'] = x_get_put_call_ratio__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_85'] = x_get_put_call_ratio__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_86'] = x_get_put_call_ratio__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_87'] = x_get_put_call_ratio__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_88'] = x_get_put_call_ratio__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_89'] = x_get_put_call_ratio__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_90'] = x_get_put_call_ratio__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_91'] = x_get_put_call_ratio__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_92'] = x_get_put_call_ratio__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_93'] = x_get_put_call_ratio__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_put_call_ratio__mutmut['x_get_put_call_ratio__mutmut_94'] = x_get_put_call_ratio__mutmut_94 # type: ignore # mutmut generated
