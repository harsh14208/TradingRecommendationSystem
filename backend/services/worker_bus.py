"""
Async Worker Bus — lightweight event-driven infrastructure for signal scoring.

Provides:
  • WorkerTask  — async function wrapper with timeout, per-source retry budget,
                  and per-source circuit breaker.
  • WorkerBus   — asyncio.Queue-based message bus (default) that swaps to Redis
                  Streams when REDIS_URL is configured, enabling cross-process
                  worker distribution with zero code changes in callers.
  • ScoringResult — typed return value shared by all 5 scoring workers.

Design principles
  1. Every external data call lives inside ONE worker. If it times out, only
     that worker's score contribution is zero — TA and other workers are unaffected.
  2. Circuit breaker per source: after N consecutive failures the breaker opens
     for RESET_SECONDS, skipping further calls and returning empty results
     immediately. This prevents piling on an already-struggling API.
  3. asyncio-first: all workers are async coroutines; no thread pools needed.
  4. Redis upgrade path: replace 'asyncio' backend with 'redis' in REDIS_URL and
     the bus transparently publishes/consumes from Redis Streams. Workers run in
     separate processes for true parallelism.
"""

import asyncio
import logging
import os
import time
from collections.abc import AsyncGenerator, Callable, Coroutine
from dataclasses import dataclass, field

log = logging.getLogger("signal.trade.worker_bus")


# ── Typed result from every scoring worker ──────────────────────────────────


@dataclass
class ScoringResult:
    score: float = 0.0
    sources: set = field(default_factory=set)
    rationale: list = field(default_factory=list)
    ok: bool = True  # False = worker timed-out or circuit-broke


# ── Circuit Breaker ──────────────────────────────────────────────────────────


class CircuitBreaker:
    """
    Simple per-source circuit breaker.
    Opens after `threshold` consecutive failures; resets after `reset_secs`.
    """

    def __init__(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def record_success(self):
        self._failures = 0
        self._opened_at = None

    def record_failure(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()


# ── WorkerTask decorator ─────────────────────────────────────────────────────


class WorkerTask:
    """
    Wraps an async scoring function with:
      - Per-invocation timeout (seconds)
      - Per-source retry budget (up to `retries` attempts with exponential backoff)
      - Circuit breaker (skips after repeated failures; self-heals after reset_secs)

    Returns ScoringResult(ok=False) on any failure — never raises.

    Usage:
        @WorkerTask(name="news", timeout=8.0, retries=2)
        async def news_worker(ticker, news, ...):
            ...
            return ScoringResult(score=..., sources={...}, rationale=[...])
    """

    def __init__(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 3,
        cb_reset_secs: float = 120.0,
    ):
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def __call__(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(1, task.retries)):
                try:
                    result = await asyncio.wait_for(
                        fn(*args, **kwargs),
                        timeout=task.timeout,
                    )
                    task._cb.record_success()
                    return result if isinstance(result, ScoringResult) else ScoringResult()
                except asyncio.TimeoutError:
                    last_exc = asyncio.TimeoutError(f"{task.name} timed out after {task.timeout}s")
                    log.debug("[worker] %s attempt %d: timeout", task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.info("[worker] %s: FAILED (%s)", task.name, last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    @property
    def stats(self) -> dict:
        return {
            "name": self.name,
            "calls": self._calls,
            "errors": self._errors,
            "error_rate": round(self._errors / max(self._calls, 1) * 100, 1),
            "circuit_open": self._cb.is_open(),
        }


# ── Worker Bus ───────────────────────────────────────────────────────────────


class WorkerBus:
    """
    Thin message-passing layer for scoring workers.

    Default backend: asyncio.Queue (in-process, zero dependencies).
    Redis backend:   activated when REDIS_URL env var is set. Workers publish
                     to Redis Streams; the coordinator reads from multiple streams
                     concurrently across processes.

    The asyncio backend is functionally equivalent but local; swap to Redis when
    you need separate worker processes (e.g., a dedicated news-scoring container).
    """

    def __init__(self):
        self._use_redis = bool(os.getenv("REDIS_URL"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def publish(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def consume(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                msgs = await r.xreadgroup(
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
                )
                if msgs:
                    for _, entries in msgs:
                        for msg_id, data in entries:
                            await r.xack(stream, group, msg_id)
                            yield data
                            return
        else:
            q = self._queues.get(stream)
            if q is None:
                return
            try:
                item = await asyncio.wait_for(q.get(), timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def close(self):
        if self._redis:
            await self._redis.aclose()
            self._redis = None


# ── Module-level bus singleton ───────────────────────────────────────────────

_bus: WorkerBus | None = None


def get_bus() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def collect_worker_stats(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_task", None)
        if task:
            stats.append(task.stats)
    return stats
