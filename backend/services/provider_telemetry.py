import contextvars
import logging
from database import AsyncSessionLocal
from models import ProviderTelemetry

log = logging.getLogger("signal.trade.telemetry")

# ContextVar to hold the current cycle ID per asyncio Task/context (TSYS-4b)
current_cycle_id = contextvars.ContextVar("current_cycle_id", default=None)

# In-memory store for accumulating telemetry during a cycle (TSYS-4d)
_telemetry_store = {}


def init_cycle_telemetry(cycle_id: str):
    if cycle_id:
        _telemetry_store[cycle_id] = {}


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
