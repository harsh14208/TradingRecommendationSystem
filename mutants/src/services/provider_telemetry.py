import contextvars
import logging
from database import AsyncSessionLocal
from models import ProviderTelemetry

log = logging.getLogger("signal.trade.telemetry")

# ContextVar to hold the current cycle ID per asyncio Task/context (TSYS-4b)
current_cycle_id = contextvars.ContextVar("current_cycle_id", default=None)

# In-memory store for accumulating telemetry during a cycle (TSYS-4d)
_telemetry_store = {}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_init_cycle_telemetry__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_init_cycle_telemetry__mutmut)
def init_cycle_telemetry(cycle_id: str):
    if cycle_id:
        _telemetry_store[cycle_id] = {}


def x_init_cycle_telemetry__mutmut_orig(cycle_id: str):
    if cycle_id:
        _telemetry_store[cycle_id] = {}


def x_init_cycle_telemetry__mutmut_1(cycle_id: str):
    if cycle_id:
        _telemetry_store[cycle_id] = None

mutants_x_init_cycle_telemetry__mutmut['_mutmut_orig'] = x_init_cycle_telemetry__mutmut_orig # type: ignore # mutmut generated
mutants_x_init_cycle_telemetry__mutmut['x_init_cycle_telemetry__mutmut_1'] = x_init_cycle_telemetry__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_record_api_call__mutmut)
def record_api_call(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_orig(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_1(cycle_id: str | None, provider: str, throttled: bool = True, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_2(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = True):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_3(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id and cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_4(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_5(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_6(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = None
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_7(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        None,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_8(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        None,
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_9(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_10(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_11(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "XXapi_callsXX": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_12(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "API_CALLS": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_13(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 1,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_14(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "XXcache_hitsXX": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_15(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "CACHE_HITS": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_16(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 1,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_17(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "XXcache_missesXX": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_18(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "CACHE_MISSES": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_19(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 1,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_20(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "XXquota_remainingXX": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_21(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "QUOTA_REMAINING": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_22(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "XXthrottlesXX": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_23(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "THROTTLES": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_24(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 1,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_25(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "XXfallback_usageXX": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_26(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "FALLBACK_USAGE": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_27(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 1,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_28(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] = 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_29(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] -= 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_30(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["XXapi_callsXX"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_31(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["API_CALLS"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_32(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 2
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_33(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] = 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_34(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] -= 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_35(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["XXthrottlesXX"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_36(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["THROTTLES"] += 1
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_37(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 2
    if fallback:
        stats["fallback_usage"] += 1


def x_record_api_call__mutmut_38(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] = 1


def x_record_api_call__mutmut_39(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] -= 1


def x_record_api_call__mutmut_40(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["XXfallback_usageXX"] += 1


def x_record_api_call__mutmut_41(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["FALLBACK_USAGE"] += 1


def x_record_api_call__mutmut_42(cycle_id: str | None, provider: str, throttled: bool = False, fallback: bool = False):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["api_calls"] += 1
    if throttled:
        stats["throttles"] += 1
    if fallback:
        stats["fallback_usage"] += 2

mutants_x_record_api_call__mutmut['_mutmut_orig'] = x_record_api_call__mutmut_orig # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_1'] = x_record_api_call__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_2'] = x_record_api_call__mutmut_2 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_3'] = x_record_api_call__mutmut_3 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_4'] = x_record_api_call__mutmut_4 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_5'] = x_record_api_call__mutmut_5 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_6'] = x_record_api_call__mutmut_6 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_7'] = x_record_api_call__mutmut_7 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_8'] = x_record_api_call__mutmut_8 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_9'] = x_record_api_call__mutmut_9 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_10'] = x_record_api_call__mutmut_10 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_11'] = x_record_api_call__mutmut_11 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_12'] = x_record_api_call__mutmut_12 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_13'] = x_record_api_call__mutmut_13 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_14'] = x_record_api_call__mutmut_14 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_15'] = x_record_api_call__mutmut_15 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_16'] = x_record_api_call__mutmut_16 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_17'] = x_record_api_call__mutmut_17 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_18'] = x_record_api_call__mutmut_18 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_19'] = x_record_api_call__mutmut_19 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_20'] = x_record_api_call__mutmut_20 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_21'] = x_record_api_call__mutmut_21 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_22'] = x_record_api_call__mutmut_22 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_23'] = x_record_api_call__mutmut_23 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_24'] = x_record_api_call__mutmut_24 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_25'] = x_record_api_call__mutmut_25 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_26'] = x_record_api_call__mutmut_26 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_27'] = x_record_api_call__mutmut_27 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_28'] = x_record_api_call__mutmut_28 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_29'] = x_record_api_call__mutmut_29 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_30'] = x_record_api_call__mutmut_30 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_31'] = x_record_api_call__mutmut_31 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_32'] = x_record_api_call__mutmut_32 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_33'] = x_record_api_call__mutmut_33 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_34'] = x_record_api_call__mutmut_34 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_35'] = x_record_api_call__mutmut_35 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_36'] = x_record_api_call__mutmut_36 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_37'] = x_record_api_call__mutmut_37 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_38'] = x_record_api_call__mutmut_38 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_39'] = x_record_api_call__mutmut_39 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_40'] = x_record_api_call__mutmut_40 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_41'] = x_record_api_call__mutmut_41 # type: ignore # mutmut generated
mutants_x_record_api_call__mutmut['x_record_api_call__mutmut_42'] = x_record_api_call__mutmut_42 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_record_cache_hit__mutmut)
def record_cache_hit(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_orig(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_1(cycle_id: str | None, provider: str):
    if not cycle_id and cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_2(cycle_id: str | None, provider: str):
    if cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_3(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_4(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = None
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_5(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        None,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_6(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        None,
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_7(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_8(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_9(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "XXapi_callsXX": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_10(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "API_CALLS": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_11(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 1,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_12(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "XXcache_hitsXX": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_13(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "CACHE_HITS": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_14(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 1,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_15(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "XXcache_missesXX": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_16(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "CACHE_MISSES": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_17(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 1,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_18(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "XXquota_remainingXX": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_19(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "QUOTA_REMAINING": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_20(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "XXthrottlesXX": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_21(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "THROTTLES": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_22(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 1,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_23(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "XXfallback_usageXX": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_24(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "FALLBACK_USAGE": 0,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_25(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 1,
        },
    )
    stats["cache_hits"] += 1


def x_record_cache_hit__mutmut_26(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] = 1


def x_record_cache_hit__mutmut_27(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] -= 1


def x_record_cache_hit__mutmut_28(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["XXcache_hitsXX"] += 1


def x_record_cache_hit__mutmut_29(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["CACHE_HITS"] += 1


def x_record_cache_hit__mutmut_30(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_hits"] += 2

mutants_x_record_cache_hit__mutmut['_mutmut_orig'] = x_record_cache_hit__mutmut_orig # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_1'] = x_record_cache_hit__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_2'] = x_record_cache_hit__mutmut_2 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_3'] = x_record_cache_hit__mutmut_3 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_4'] = x_record_cache_hit__mutmut_4 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_5'] = x_record_cache_hit__mutmut_5 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_6'] = x_record_cache_hit__mutmut_6 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_7'] = x_record_cache_hit__mutmut_7 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_8'] = x_record_cache_hit__mutmut_8 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_9'] = x_record_cache_hit__mutmut_9 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_10'] = x_record_cache_hit__mutmut_10 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_11'] = x_record_cache_hit__mutmut_11 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_12'] = x_record_cache_hit__mutmut_12 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_13'] = x_record_cache_hit__mutmut_13 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_14'] = x_record_cache_hit__mutmut_14 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_15'] = x_record_cache_hit__mutmut_15 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_16'] = x_record_cache_hit__mutmut_16 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_17'] = x_record_cache_hit__mutmut_17 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_18'] = x_record_cache_hit__mutmut_18 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_19'] = x_record_cache_hit__mutmut_19 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_20'] = x_record_cache_hit__mutmut_20 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_21'] = x_record_cache_hit__mutmut_21 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_22'] = x_record_cache_hit__mutmut_22 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_23'] = x_record_cache_hit__mutmut_23 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_24'] = x_record_cache_hit__mutmut_24 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_25'] = x_record_cache_hit__mutmut_25 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_26'] = x_record_cache_hit__mutmut_26 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_27'] = x_record_cache_hit__mutmut_27 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_28'] = x_record_cache_hit__mutmut_28 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_29'] = x_record_cache_hit__mutmut_29 # type: ignore # mutmut generated
mutants_x_record_cache_hit__mutmut['x_record_cache_hit__mutmut_30'] = x_record_cache_hit__mutmut_30 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_record_cache_miss__mutmut)
def record_cache_miss(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_orig(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_1(cycle_id: str | None, provider: str):
    if not cycle_id and cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_2(cycle_id: str | None, provider: str):
    if cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_3(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_4(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = None
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_5(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        None,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_6(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        None,
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_7(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_8(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_9(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "XXapi_callsXX": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_10(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "API_CALLS": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_11(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 1,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_12(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "XXcache_hitsXX": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_13(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "CACHE_HITS": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_14(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 1,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_15(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "XXcache_missesXX": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_16(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "CACHE_MISSES": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_17(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 1,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_18(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "XXquota_remainingXX": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_19(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "QUOTA_REMAINING": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_20(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "XXthrottlesXX": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_21(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "THROTTLES": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_22(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 1,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_23(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "XXfallback_usageXX": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_24(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "FALLBACK_USAGE": 0,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_25(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 1,
        },
    )
    stats["cache_misses"] += 1


def x_record_cache_miss__mutmut_26(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] = 1


def x_record_cache_miss__mutmut_27(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] -= 1


def x_record_cache_miss__mutmut_28(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["XXcache_missesXX"] += 1


def x_record_cache_miss__mutmut_29(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["CACHE_MISSES"] += 1


def x_record_cache_miss__mutmut_30(cycle_id: str | None, provider: str):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["cache_misses"] += 2

mutants_x_record_cache_miss__mutmut['_mutmut_orig'] = x_record_cache_miss__mutmut_orig # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_1'] = x_record_cache_miss__mutmut_1 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_2'] = x_record_cache_miss__mutmut_2 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_3'] = x_record_cache_miss__mutmut_3 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_4'] = x_record_cache_miss__mutmut_4 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_5'] = x_record_cache_miss__mutmut_5 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_6'] = x_record_cache_miss__mutmut_6 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_7'] = x_record_cache_miss__mutmut_7 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_8'] = x_record_cache_miss__mutmut_8 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_9'] = x_record_cache_miss__mutmut_9 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_10'] = x_record_cache_miss__mutmut_10 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_11'] = x_record_cache_miss__mutmut_11 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_12'] = x_record_cache_miss__mutmut_12 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_13'] = x_record_cache_miss__mutmut_13 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_14'] = x_record_cache_miss__mutmut_14 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_15'] = x_record_cache_miss__mutmut_15 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_16'] = x_record_cache_miss__mutmut_16 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_17'] = x_record_cache_miss__mutmut_17 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_18'] = x_record_cache_miss__mutmut_18 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_19'] = x_record_cache_miss__mutmut_19 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_20'] = x_record_cache_miss__mutmut_20 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_21'] = x_record_cache_miss__mutmut_21 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_22'] = x_record_cache_miss__mutmut_22 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_23'] = x_record_cache_miss__mutmut_23 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_24'] = x_record_cache_miss__mutmut_24 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_25'] = x_record_cache_miss__mutmut_25 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_26'] = x_record_cache_miss__mutmut_26 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_27'] = x_record_cache_miss__mutmut_27 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_28'] = x_record_cache_miss__mutmut_28 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_29'] = x_record_cache_miss__mutmut_29 # type: ignore # mutmut generated
mutants_x_record_cache_miss__mutmut['x_record_cache_miss__mutmut_30'] = x_record_cache_miss__mutmut_30 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_update_quota__mutmut)
def update_quota(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_orig(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_1(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id and cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_2(cycle_id: str | None, provider: str, quota: int):
    if cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_3(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_4(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = None
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_5(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        None,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_6(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        None,
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_7(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_8(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_9(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "XXapi_callsXX": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_10(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "API_CALLS": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_11(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 1,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_12(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "XXcache_hitsXX": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_13(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "CACHE_HITS": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_14(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 1,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_15(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "XXcache_missesXX": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_16(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "CACHE_MISSES": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_17(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 1,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_18(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "XXquota_remainingXX": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_19(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "QUOTA_REMAINING": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_20(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "XXthrottlesXX": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_21(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "THROTTLES": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_22(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 1,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_23(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "XXfallback_usageXX": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_24(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "FALLBACK_USAGE": 0,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_25(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 1,
        },
    )
    stats["quota_remaining"] = quota


def x_update_quota__mutmut_26(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["quota_remaining"] = None


def x_update_quota__mutmut_27(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["XXquota_remainingXX"] = quota


def x_update_quota__mutmut_28(cycle_id: str | None, provider: str, quota: int):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    stats = _telemetry_store[cycle_id].setdefault(
        provider,
        {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "quota_remaining": None,
            "throttles": 0,
            "fallback_usage": 0,
        },
    )
    stats["QUOTA_REMAINING"] = quota

mutants_x_update_quota__mutmut['_mutmut_orig'] = x_update_quota__mutmut_orig # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_1'] = x_update_quota__mutmut_1 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_2'] = x_update_quota__mutmut_2 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_3'] = x_update_quota__mutmut_3 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_4'] = x_update_quota__mutmut_4 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_5'] = x_update_quota__mutmut_5 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_6'] = x_update_quota__mutmut_6 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_7'] = x_update_quota__mutmut_7 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_8'] = x_update_quota__mutmut_8 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_9'] = x_update_quota__mutmut_9 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_10'] = x_update_quota__mutmut_10 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_11'] = x_update_quota__mutmut_11 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_12'] = x_update_quota__mutmut_12 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_13'] = x_update_quota__mutmut_13 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_14'] = x_update_quota__mutmut_14 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_15'] = x_update_quota__mutmut_15 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_16'] = x_update_quota__mutmut_16 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_17'] = x_update_quota__mutmut_17 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_18'] = x_update_quota__mutmut_18 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_19'] = x_update_quota__mutmut_19 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_20'] = x_update_quota__mutmut_20 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_21'] = x_update_quota__mutmut_21 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_22'] = x_update_quota__mutmut_22 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_23'] = x_update_quota__mutmut_23 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_24'] = x_update_quota__mutmut_24 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_25'] = x_update_quota__mutmut_25 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_26'] = x_update_quota__mutmut_26 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_27'] = x_update_quota__mutmut_27 # type: ignore # mutmut generated
mutants_x_update_quota__mutmut['x_update_quota__mutmut_28'] = x_update_quota__mutmut_28 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_flush_cycle_telemetry__mutmut)
async def flush_cycle_telemetry(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_orig(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_1(cycle_id: str | None):
    if not cycle_id and cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_2(cycle_id: str | None):
    if cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_3(cycle_id: str | None):
    if not cycle_id or cycle_id in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_4(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = None
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_5(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(None)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_6(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = None
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_7(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=None,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_8(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=None,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_9(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=None,
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_10(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=None,
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_11(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=None,
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_12(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=None,
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_13(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=None,
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_14(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=None,
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_15(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_16(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_17(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_18(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_19(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_20(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_21(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_22(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_23(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["XXapi_callsXX"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_24(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["API_CALLS"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_25(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["XXcache_hitsXX"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_26(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["CACHE_HITS"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_27(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["XXcache_missesXX"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_28(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["CACHE_MISSES"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_29(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["XXquota_remainingXX"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_30(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["QUOTA_REMAINING"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_31(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["XXthrottlesXX"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_32(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["THROTTLES"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_33(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["XXfallback_usageXX"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_34(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["FALLBACK_USAGE"],
            )
            db.add(telemetry)
        await db.commit()


async def x_flush_cycle_telemetry__mutmut_35(cycle_id: str | None):
    if not cycle_id or cycle_id not in _telemetry_store:
        return
    prov_data = _telemetry_store.pop(cycle_id)
    async with AsyncSessionLocal() as db:
        for provider, stats in prov_data.items():
            telemetry = ProviderTelemetry(
                cycle_id=cycle_id,
                provider=provider,
                api_calls=stats["api_calls"],
                cache_hits=stats["cache_hits"],
                cache_misses=stats["cache_misses"],
                quota_remaining=stats["quota_remaining"],
                throttles=stats["throttles"],
                fallback_usage=stats["fallback_usage"],
            )
            db.add(None)
        await db.commit()

mutants_x_flush_cycle_telemetry__mutmut['_mutmut_orig'] = x_flush_cycle_telemetry__mutmut_orig # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_1'] = x_flush_cycle_telemetry__mutmut_1 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_2'] = x_flush_cycle_telemetry__mutmut_2 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_3'] = x_flush_cycle_telemetry__mutmut_3 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_4'] = x_flush_cycle_telemetry__mutmut_4 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_5'] = x_flush_cycle_telemetry__mutmut_5 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_6'] = x_flush_cycle_telemetry__mutmut_6 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_7'] = x_flush_cycle_telemetry__mutmut_7 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_8'] = x_flush_cycle_telemetry__mutmut_8 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_9'] = x_flush_cycle_telemetry__mutmut_9 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_10'] = x_flush_cycle_telemetry__mutmut_10 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_11'] = x_flush_cycle_telemetry__mutmut_11 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_12'] = x_flush_cycle_telemetry__mutmut_12 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_13'] = x_flush_cycle_telemetry__mutmut_13 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_14'] = x_flush_cycle_telemetry__mutmut_14 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_15'] = x_flush_cycle_telemetry__mutmut_15 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_16'] = x_flush_cycle_telemetry__mutmut_16 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_17'] = x_flush_cycle_telemetry__mutmut_17 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_18'] = x_flush_cycle_telemetry__mutmut_18 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_19'] = x_flush_cycle_telemetry__mutmut_19 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_20'] = x_flush_cycle_telemetry__mutmut_20 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_21'] = x_flush_cycle_telemetry__mutmut_21 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_22'] = x_flush_cycle_telemetry__mutmut_22 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_23'] = x_flush_cycle_telemetry__mutmut_23 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_24'] = x_flush_cycle_telemetry__mutmut_24 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_25'] = x_flush_cycle_telemetry__mutmut_25 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_26'] = x_flush_cycle_telemetry__mutmut_26 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_27'] = x_flush_cycle_telemetry__mutmut_27 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_28'] = x_flush_cycle_telemetry__mutmut_28 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_29'] = x_flush_cycle_telemetry__mutmut_29 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_30'] = x_flush_cycle_telemetry__mutmut_30 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_31'] = x_flush_cycle_telemetry__mutmut_31 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_32'] = x_flush_cycle_telemetry__mutmut_32 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_33'] = x_flush_cycle_telemetry__mutmut_33 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_34'] = x_flush_cycle_telemetry__mutmut_34 # type: ignore # mutmut generated
mutants_x_flush_cycle_telemetry__mutmut['x_flush_cycle_telemetry__mutmut_35'] = x_flush_cycle_telemetry__mutmut_35 # type: ignore # mutmut generated
