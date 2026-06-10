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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


# ── Typed result from every scoring worker ──────────────────────────────────


@dataclass
class ScoringResult:
    score: float = 0.0
    sources: set = field(default_factory=set)
    rationale: list = field(default_factory=list)
    ok: bool = True  # False = worker timed-out or circuit-broke
mutants_xǁCircuitBreakerǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁCircuitBreakerǁis_open__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCircuitBreakerǁrecord_success__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCircuitBreakerǁrecord_failure__mutmut: MutantDict = {}  # type: ignore


# ── Circuit Breaker ──────────────────────────────────────────────────────────


class CircuitBreaker:
    """
    Simple per-source circuit breaker.
    Opens after `threshold` consecutive failures; resets after `reset_secs`.
    """

    @_mutmut_mutated(mutants_xǁCircuitBreakerǁ__init____mutmut)
    def __init__(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_orig(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_1(self, name: str, threshold: int = 4, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_2(self, name: str, threshold: int = 3, reset_secs: float = 121.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_3(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = None
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_4(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = None
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_5(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = None
        self._failures = 0
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_6(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = None
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_7(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 1
        self._opened_at: float | None = None

    def xǁCircuitBreakerǁ__init____mutmut_8(self, name: str, threshold: int = 3, reset_secs: float = 120.0):
        self.name = name
        self.threshold = threshold
        self.reset_secs = reset_secs
        self._failures = 0
        self._opened_at: float | None = ""

    @_mutmut_mutated(mutants_xǁCircuitBreakerǁis_open__mutmut)
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_orig(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_1(self) -> bool:
        if self._opened_at is not None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_2(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_3(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() + self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_4(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at > self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_5(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info(None, self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_6(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", None, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_7(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, None)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_8(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info(self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_9(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_10(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, )
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_11(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("XX[circuit] %s: reset after %.0fsXX", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_12(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[CIRCUIT] %S: RESET AFTER %.0FS", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_13(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = None
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_14(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 1
            self._opened_at = None
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_15(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = ""
            return False
        return True

    def xǁCircuitBreakerǁis_open__mutmut_16(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return True
        return True

    def xǁCircuitBreakerǁis_open__mutmut_17(self) -> bool:
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.reset_secs:
            log.info("[circuit] %s: reset after %.0fs", self.name, self.reset_secs)
            self._failures = 0
            self._opened_at = None
            return False
        return False

    @_mutmut_mutated(mutants_xǁCircuitBreakerǁrecord_success__mutmut)
    def record_success(self):
        self._failures = 0
        self._opened_at = None

    def xǁCircuitBreakerǁrecord_success__mutmut_orig(self):
        self._failures = 0
        self._opened_at = None

    def xǁCircuitBreakerǁrecord_success__mutmut_1(self):
        self._failures = None
        self._opened_at = None

    def xǁCircuitBreakerǁrecord_success__mutmut_2(self):
        self._failures = 1
        self._opened_at = None

    def xǁCircuitBreakerǁrecord_success__mutmut_3(self):
        self._failures = 0
        self._opened_at = ""

    @_mutmut_mutated(mutants_xǁCircuitBreakerǁrecord_failure__mutmut)
    def record_failure(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_orig(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_1(self):
        self._failures = 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_2(self):
        self._failures -= 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_3(self):
        self._failures += 2
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_4(self):
        self._failures += 1
        if self._failures > self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_5(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is not None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_6(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning(None, self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_7(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", None, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_8(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, None)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_9(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning(self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_10(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_11(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, )
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_12(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("XX[circuit] %s: OPEN after %d failuresXX", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_13(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: open after %d failures", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_14(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[CIRCUIT] %S: OPEN AFTER %D FAILURES", self.name, self._failures)
            self._opened_at = time.monotonic()

    def xǁCircuitBreakerǁrecord_failure__mutmut_15(self):
        self._failures += 1
        if self._failures >= self.threshold:
            if self._opened_at is None:
                log.warning("[circuit] %s: OPEN after %d failures", self.name, self._failures)
            self._opened_at = None

mutants_xǁCircuitBreakerǁ__init____mutmut['_mutmut_orig'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_1'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_2'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_3'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_4'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_5'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_6'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_7'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁ__init____mutmut['xǁCircuitBreakerǁ__init____mutmut_8'] = CircuitBreaker.xǁCircuitBreakerǁ__init____mutmut_8 # type: ignore # mutmut generated

mutants_xǁCircuitBreakerǁis_open__mutmut['_mutmut_orig'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_1'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_2'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_3'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_4'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_5'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_6'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_7'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_8'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_9'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_10'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_11'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_12'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_13'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_14'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_15'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_16'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁis_open__mutmut['xǁCircuitBreakerǁis_open__mutmut_17'] = CircuitBreaker.xǁCircuitBreakerǁis_open__mutmut_17 # type: ignore # mutmut generated

mutants_xǁCircuitBreakerǁrecord_success__mutmut['_mutmut_orig'] = CircuitBreaker.xǁCircuitBreakerǁrecord_success__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_success__mutmut['xǁCircuitBreakerǁrecord_success__mutmut_1'] = CircuitBreaker.xǁCircuitBreakerǁrecord_success__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_success__mutmut['xǁCircuitBreakerǁrecord_success__mutmut_2'] = CircuitBreaker.xǁCircuitBreakerǁrecord_success__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_success__mutmut['xǁCircuitBreakerǁrecord_success__mutmut_3'] = CircuitBreaker.xǁCircuitBreakerǁrecord_success__mutmut_3 # type: ignore # mutmut generated

mutants_xǁCircuitBreakerǁrecord_failure__mutmut['_mutmut_orig'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_1'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_2'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_3'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_4'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_5'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_6'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_7'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_8'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_9'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_10'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_11'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_12'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_13'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_14'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCircuitBreakerǁrecord_failure__mutmut['xǁCircuitBreakerǁrecord_failure__mutmut_15'] = CircuitBreaker.xǁCircuitBreakerǁrecord_failure__mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁWorkerTaskǁ__call____mutmut: MutantDict = {}  # type: ignore


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

    @_mutmut_mutated(mutants_xǁWorkerTaskǁ__init____mutmut)
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

    def xǁWorkerTaskǁ__init____mutmut_orig(
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

    def xǁWorkerTaskǁ__init____mutmut_1(
        self,
        name: str,
        timeout: float = 11.0,
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

    def xǁWorkerTaskǁ__init____mutmut_2(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 2,
        cb_threshold: int = 3,
        cb_reset_secs: float = 120.0,
    ):
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_3(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 4,
        cb_reset_secs: float = 120.0,
    ):
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_4(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 3,
        cb_reset_secs: float = 121.0,
    ):
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_5(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 3,
        cb_reset_secs: float = 120.0,
    ):
        self.name = None
        self.timeout = timeout
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_6(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 3,
        cb_reset_secs: float = 120.0,
    ):
        self.name = name
        self.timeout = None
        self.retries = retries
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_7(
        self,
        name: str,
        timeout: float = 10.0,
        retries: int = 1,
        cb_threshold: int = 3,
        cb_reset_secs: float = 120.0,
    ):
        self.name = name
        self.timeout = timeout
        self.retries = None
        self._cb = CircuitBreaker(name, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_8(
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
        self._cb = None
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_9(
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
        self._cb = CircuitBreaker(None, cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_10(
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
        self._cb = CircuitBreaker(name, None, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_11(
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
        self._cb = CircuitBreaker(name, cb_threshold, None)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_12(
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
        self._cb = CircuitBreaker(cb_threshold, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_13(
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
        self._cb = CircuitBreaker(name, cb_reset_secs)
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_14(
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
        self._cb = CircuitBreaker(name, cb_threshold, )
        self._calls = 0
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_15(
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
        self._calls = None
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_16(
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
        self._calls = 1
        self._errors = 0

    def xǁWorkerTaskǁ__init____mutmut_17(
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
        self._errors = None

    def xǁWorkerTaskǁ__init____mutmut_18(
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
        self._errors = 1

    @_mutmut_mutated(mutants_xǁWorkerTaskǁ__call____mutmut)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_orig(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_1(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = None  # capture for the closure

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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_2(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug(None, task.name)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_3(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", None)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_4(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug(task.name)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_5(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", )
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_6(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("XX[worker] %s: circuit open — skippingXX", task.name)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_7(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[WORKER] %S: CIRCUIT OPEN — SKIPPING", task.name)
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_8(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=None)

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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_9(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=True)

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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_10(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls = 1
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_11(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls -= 1
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_12(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 2
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_13(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = ""

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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_14(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(None):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_15(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(None, task.retries)):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_16(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(1, None)):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_17(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(task.retries)):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_18(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(1, )):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_19(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(2, task.retries)):
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_20(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        task = self  # capture for the closure

        async def wrapper(*args, **kwargs) -> ScoringResult:
            if task._cb.is_open():
                log.debug("[worker] %s: circuit open — skipping", task.name)
                return ScoringResult(ok=False)

            task._calls += 1
            last_exc: Exception | None = None

            for attempt in range(max(1, task.retries)):
                try:
                    result = None
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_21(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                        None,
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_22(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                        timeout=None,
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_23(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_24(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_25(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                        fn(**kwargs),
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_26(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                        fn(*args, ),
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_27(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    last_exc = None
                    log.debug("[worker] %s attempt %d: timeout", task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_28(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    last_exc = asyncio.TimeoutError(None)
                    log.debug("[worker] %s attempt %d: timeout", task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_29(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug(None, task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_30(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", None, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_31(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", task.name, None)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_32(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug(task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_33(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_34(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", task.name, )
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_35(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("XX[worker] %s attempt %d: timeoutXX", task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_36(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[WORKER] %S ATTEMPT %D: TIMEOUT", task.name, attempt + 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_37(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", task.name, attempt - 1)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_38(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: timeout", task.name, attempt + 2)
                except Exception as e:
                    last_exc = e
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_39(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    last_exc = None
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_40(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug(None, task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_41(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", None, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_42(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, None, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_43(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, None)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_44(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug(task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_45(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_46(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_47(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 1, )

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_48(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("XX[worker] %s attempt %d: %sXX", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_49(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[WORKER] %S ATTEMPT %D: %S", task.name, attempt + 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_50(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt - 1, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_51(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    log.debug("[worker] %s attempt %d: %s", task.name, attempt + 2, e)

                if attempt < task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_52(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

                if attempt <= task.retries - 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_53(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

                if attempt < task.retries + 1:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_54(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

                if attempt < task.retries - 2:
                    await asyncio.sleep(0.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_55(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    await asyncio.sleep(None)  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_56(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    await asyncio.sleep(0.5 / (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_57(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    await asyncio.sleep(1.5 * (2**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_58(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    await asyncio.sleep(0.5 * (2 * attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_59(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
                    await asyncio.sleep(0.5 * (3**attempt))  # 0.5s, 1s, 2s…

            task._errors += 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_60(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

            task._errors = 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_61(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

            task._errors -= 1
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_62(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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

            task._errors += 2
            task._cb.record_failure()
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_63(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning(None, task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_64(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", None, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_65(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, None, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_66(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=None)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_67(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning(task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_68(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_69(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_70(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, )
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_71(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("XX[worker] %s: FAILED (%s)XX", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_72(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: failed (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_73(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[WORKER] %S: FAILED (%S)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_74(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=None)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_75(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=True)

        wrapper.__name__ = fn.__name__
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_76(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = None
        wrapper._task = task  # expose for introspection
        return wrapper

    def xǁWorkerTaskǁ__call____mutmut_77(self, fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
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
            log.warning("[worker] %s: FAILED (%s)", task.name, last_exc, exc_info=last_exc)
            return ScoringResult(ok=False)

        wrapper.__name__ = fn.__name__
        wrapper._task = None  # expose for introspection
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

mutants_xǁWorkerTaskǁ__init____mutmut['_mutmut_orig'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_1'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_2'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_3'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_4'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_5'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_6'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_7'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_8'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_9'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_10'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_11'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_12'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_13'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_14'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_15'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_16'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_17'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__init____mutmut['xǁWorkerTaskǁ__init____mutmut_18'] = WorkerTask.xǁWorkerTaskǁ__init____mutmut_18 # type: ignore # mutmut generated

mutants_xǁWorkerTaskǁ__call____mutmut['_mutmut_orig'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_1'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_2'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_3'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_4'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_5'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_6'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_7'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_7 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_8'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_8 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_9'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_9 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_10'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_10 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_11'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_11 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_12'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_12 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_13'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_13 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_14'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_14 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_15'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_16'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_16 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_17'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_17 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_18'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_18 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_19'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_19 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_20'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_20 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_21'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_21 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_22'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_22 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_23'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_23 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_24'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_24 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_25'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_25 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_26'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_26 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_27'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_27 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_28'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_28 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_29'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_29 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_30'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_30 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_31'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_31 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_32'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_32 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_33'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_33 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_34'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_34 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_35'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_35 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_36'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_36 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_37'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_37 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_38'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_38 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_39'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_39 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_40'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_40 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_41'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_41 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_42'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_42 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_43'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_43 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_44'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_44 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_45'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_45 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_46'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_46 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_47'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_47 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_48'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_48 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_49'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_49 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_50'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_50 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_51'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_51 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_52'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_52 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_53'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_53 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_54'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_54 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_55'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_55 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_56'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_56 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_57'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_57 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_58'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_58 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_59'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_59 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_60'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_60 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_61'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_61 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_62'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_62 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_63'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_63 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_64'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_64 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_65'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_65 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_66'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_66 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_67'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_67 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_68'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_68 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_69'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_69 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_70'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_70 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_71'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_71 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_72'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_72 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_73'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_73 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_74'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_74 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_75'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_75 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_76'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_76 # type: ignore # mutmut generated
mutants_xǁWorkerTaskǁ__call____mutmut['xǁWorkerTaskǁ__call____mutmut_77'] = WorkerTask.xǁWorkerTaskǁ__call____mutmut_77 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁWorkerBusǁ_get_redis__mutmut: MutantDict = {}  # type: ignore
mutants_xǁWorkerBusǁpublish__mutmut: MutantDict = {}  # type: ignore
mutants_xǁWorkerBusǁconsume__mutmut: MutantDict = {}  # type: ignore
mutants_xǁWorkerBusǁclose__mutmut: MutantDict = {}  # type: ignore


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

    @_mutmut_mutated(mutants_xǁWorkerBusǁ__init____mutmut)
    def __init__(self):
        self._use_redis = bool(os.getenv("REDIS_URL"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_orig(self):
        self._use_redis = bool(os.getenv("REDIS_URL"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_1(self):
        self._use_redis = None
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_2(self):
        self._use_redis = bool(None)
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_3(self):
        self._use_redis = bool(os.getenv(None))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_4(self):
        self._use_redis = bool(os.getenv("XXREDIS_URLXX"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_5(self):
        self._use_redis = bool(os.getenv("redis_url"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_6(self):
        self._use_redis = bool(os.getenv("REDIS_URL"))
        self._queues: dict[str, asyncio.Queue] = None
        self._redis = None

    def xǁWorkerBusǁ__init____mutmut_7(self):
        self._use_redis = bool(os.getenv("REDIS_URL"))
        self._queues: dict[str, asyncio.Queue] = {}
        self._redis = ""

    @_mutmut_mutated(mutants_xǁWorkerBusǁ_get_redis__mutmut)
    async def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_orig(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_1(self):
        if self._redis is not None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_2(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = None
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_3(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                None,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_4(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding=None,
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_5(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=None,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_6(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_7(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_8(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_9(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv(None, "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_10(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", None),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_11(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_12(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", ),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_13(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("XXREDIS_URLXX", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_14(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("redis_url", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_15(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "XXredis://localhost:6379XX"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_16(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "REDIS://LOCALHOST:6379"),
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_17(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="XXutf-8XX",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_18(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="UTF-8",
                decode_responses=True,
            )
        return self._redis

    async def xǁWorkerBusǁ_get_redis__mutmut_19(self):
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=False,
            )
        return self._redis

    @_mutmut_mutated(mutants_xǁWorkerBusǁpublish__mutmut)
    async def publish(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_orig(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_1(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = None
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_2(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(None, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_3(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, None, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_4(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=None, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_5(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=None)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_6(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_7(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_8(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_9(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, )
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_10(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1001, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_11(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=False)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_12(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_13(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = None
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_14(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=None)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_15(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=201)
            await self._queues[stream].put(payload)

    async def xǁWorkerBusǁpublish__mutmut_16(self, stream: str, payload: dict) -> None:
        if self._use_redis:
            r = await self._get_redis()
            await r.xadd(stream, payload, maxlen=1000, approximate=True)
        else:
            if stream not in self._queues:
                self._queues[stream] = asyncio.Queue(maxsize=200)
            await self._queues[stream].put(None)

    @_mutmut_mutated(mutants_xǁWorkerBusǁconsume__mutmut)
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

    async def xǁWorkerBusǁconsume__mutmut_orig(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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

    async def xǁWorkerBusǁconsume__mutmut_1(self, stream: str, timeout: float = 6.0) -> AsyncGenerator[dict, None]:
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

    async def xǁWorkerBusǁconsume__mutmut_2(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = None
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

    async def xǁWorkerBusǁconsume__mutmut_3(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = None
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

    async def xǁWorkerBusǁconsume__mutmut_4(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "XXsignal_engineXX"
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

    async def xǁWorkerBusǁconsume__mutmut_5(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "SIGNAL_ENGINE"
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

    async def xǁWorkerBusǁconsume__mutmut_6(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(None, group, id="0", mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_7(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, None, id="0", mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_8(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id=None, mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_9(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=None)
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

    async def xǁWorkerBusǁconsume__mutmut_10(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(group, id="0", mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_11(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, id="0", mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_12(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_13(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", )
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

    async def xǁWorkerBusǁconsume__mutmut_14(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="XX0XX", mkstream=True)
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

    async def xǁWorkerBusǁconsume__mutmut_15(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=False)
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

    async def xǁWorkerBusǁconsume__mutmut_16(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = None
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

    async def xǁWorkerBusǁconsume__mutmut_17(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = time.monotonic() - timeout
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

    async def xǁWorkerBusǁconsume__mutmut_18(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = time.monotonic() + timeout
            while time.monotonic() <= deadline:
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

    async def xǁWorkerBusǁconsume__mutmut_19(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = None
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

    async def xǁWorkerBusǁconsume__mutmut_20(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
        if self._use_redis:
            r = await self._get_redis()
            group = "signal_engine"
            try:
                await r.xgroup_create(stream, group, id="0", mkstream=True)
            except Exception:
                pass  # group already exists
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = deadline + time.monotonic()
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

    async def xǁWorkerBusǁconsume__mutmut_21(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                msgs = None
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

    async def xǁWorkerBusǁconsume__mutmut_22(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    None, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_23(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, None, {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_24(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", None, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_25(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=None, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_26(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=None
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

    async def xǁWorkerBusǁconsume__mutmut_27(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_28(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_29(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_30(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_31(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, )
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

    async def xǁWorkerBusǁconsume__mutmut_32(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "XXworker-1XX", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_33(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "WORKER-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_34(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: "XX>XX"}, count=1, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_35(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=2, block=int(min(remaining, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_36(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(None)
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

    async def xǁWorkerBusǁconsume__mutmut_37(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) / 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_38(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(None, 1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_39(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, None) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_40(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(1.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_41(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, ) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_42(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 2.0) * 1000)
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

    async def xǁWorkerBusǁconsume__mutmut_43(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                    group, "worker-1", {stream: ">"}, count=1, block=int(min(remaining, 1.0) * 1001)
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

    async def xǁWorkerBusǁconsume__mutmut_44(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(None, group, msg_id)
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

    async def xǁWorkerBusǁconsume__mutmut_45(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(stream, None, msg_id)
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

    async def xǁWorkerBusǁconsume__mutmut_46(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(stream, group, None)
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

    async def xǁWorkerBusǁconsume__mutmut_47(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(group, msg_id)
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

    async def xǁWorkerBusǁconsume__mutmut_48(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(stream, msg_id)
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

    async def xǁWorkerBusǁconsume__mutmut_49(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                            await r.xack(stream, group, )
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

    async def xǁWorkerBusǁconsume__mutmut_50(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
            q = None
            if q is None:
                return
            try:
                item = await asyncio.wait_for(q.get(), timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_51(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
            q = self._queues.get(None)
            if q is None:
                return
            try:
                item = await asyncio.wait_for(q.get(), timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_52(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
            if q is not None:
                return
            try:
                item = await asyncio.wait_for(q.get(), timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_53(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                item = None
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_54(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                item = await asyncio.wait_for(None, timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_55(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                item = await asyncio.wait_for(q.get(), timeout=None)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_56(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                item = await asyncio.wait_for(timeout=timeout)
                yield item
            except asyncio.TimeoutError:
                return

    async def xǁWorkerBusǁconsume__mutmut_57(self, stream: str, timeout: float = 5.0) -> AsyncGenerator[dict, None]:
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
                item = await asyncio.wait_for(q.get(), )
                yield item
            except asyncio.TimeoutError:
                return

    @_mutmut_mutated(mutants_xǁWorkerBusǁclose__mutmut)
    async def close(self):
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def xǁWorkerBusǁclose__mutmut_orig(self):
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def xǁWorkerBusǁclose__mutmut_1(self):
        if self._redis:
            await self._redis.aclose()
            self._redis = ""

mutants_xǁWorkerBusǁ__init____mutmut['_mutmut_orig'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_1'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_2'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_3'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_4'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_5'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_6'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ__init____mutmut['xǁWorkerBusǁ__init____mutmut_7'] = WorkerBus.xǁWorkerBusǁ__init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁWorkerBusǁ_get_redis__mutmut['_mutmut_orig'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_1'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_2'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_3'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_4'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_5'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_6'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_7'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_7 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_8'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_8 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_9'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_9 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_10'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_10 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_11'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_11 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_12'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_12 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_13'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_13 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_14'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_14 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_15'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_16'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_16 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_17'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_17 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_18'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_18 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁ_get_redis__mutmut['xǁWorkerBusǁ_get_redis__mutmut_19'] = WorkerBus.xǁWorkerBusǁ_get_redis__mutmut_19 # type: ignore # mutmut generated

mutants_xǁWorkerBusǁpublish__mutmut['_mutmut_orig'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_1'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_2'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_3'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_4'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_5'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_6'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_7'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_7 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_8'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_8 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_9'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_9 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_10'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_10 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_11'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_11 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_12'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_12 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_13'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_13 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_14'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_14 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_15'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁpublish__mutmut['xǁWorkerBusǁpublish__mutmut_16'] = WorkerBus.xǁWorkerBusǁpublish__mutmut_16 # type: ignore # mutmut generated

mutants_xǁWorkerBusǁconsume__mutmut['_mutmut_orig'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_1'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_1 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_2'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_2 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_3'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_3 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_4'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_4 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_5'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_5 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_6'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_6 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_7'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_7 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_8'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_8 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_9'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_9 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_10'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_10 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_11'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_11 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_12'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_12 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_13'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_13 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_14'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_14 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_15'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_15 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_16'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_16 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_17'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_17 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_18'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_18 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_19'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_19 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_20'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_20 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_21'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_21 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_22'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_22 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_23'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_23 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_24'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_24 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_25'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_25 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_26'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_26 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_27'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_27 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_28'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_28 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_29'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_29 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_30'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_30 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_31'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_31 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_32'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_32 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_33'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_33 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_34'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_34 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_35'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_35 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_36'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_36 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_37'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_37 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_38'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_38 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_39'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_39 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_40'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_40 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_41'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_41 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_42'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_42 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_43'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_43 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_44'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_44 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_45'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_45 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_46'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_46 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_47'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_47 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_48'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_48 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_49'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_49 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_50'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_50 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_51'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_51 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_52'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_52 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_53'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_53 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_54'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_54 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_55'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_55 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_56'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_56 # type: ignore # mutmut generated
mutants_xǁWorkerBusǁconsume__mutmut['xǁWorkerBusǁconsume__mutmut_57'] = WorkerBus.xǁWorkerBusǁconsume__mutmut_57 # type: ignore # mutmut generated

mutants_xǁWorkerBusǁclose__mutmut['_mutmut_orig'] = WorkerBus.xǁWorkerBusǁclose__mutmut_orig # type: ignore # mutmut generated
mutants_xǁWorkerBusǁclose__mutmut['xǁWorkerBusǁclose__mutmut_1'] = WorkerBus.xǁWorkerBusǁclose__mutmut_1 # type: ignore # mutmut generated


# ── Module-level bus singleton ───────────────────────────────────────────────

_bus: WorkerBus | None = None
mutants_x_get_bus__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_bus__mutmut)
def get_bus() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_orig() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_1() -> WorkerBus:
    global _bus
    if _bus is not None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_2() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = None
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_3() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv(None):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_4() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("XXREDIS_URLXX"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_5() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("redis_url"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_6() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info(None, os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_7() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", None)
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_8() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info(os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_9() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", )
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_10() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("XX[worker_bus] Redis backend: %sXX", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_11() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_12() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[WORKER_BUS] REDIS BACKEND: %S", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_13() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv(None))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_14() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("XXREDIS_URLXX"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_15() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("redis_url"))
        else:
            log.info("[worker_bus] asyncio.Queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_16() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info(None)
    return _bus


def x_get_bus__mutmut_17() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("XX[worker_bus] asyncio.Queue backend (single-process)XX")
    return _bus


def x_get_bus__mutmut_18() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[worker_bus] asyncio.queue backend (single-process)")
    return _bus


def x_get_bus__mutmut_19() -> WorkerBus:
    global _bus
    if _bus is None:
        _bus = WorkerBus()
        if os.getenv("REDIS_URL"):
            log.info("[worker_bus] Redis backend: %s", os.getenv("REDIS_URL"))
        else:
            log.info("[WORKER_BUS] ASYNCIO.QUEUE BACKEND (SINGLE-PROCESS)")
    return _bus

mutants_x_get_bus__mutmut['_mutmut_orig'] = x_get_bus__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_1'] = x_get_bus__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_2'] = x_get_bus__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_3'] = x_get_bus__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_4'] = x_get_bus__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_5'] = x_get_bus__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_6'] = x_get_bus__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_7'] = x_get_bus__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_8'] = x_get_bus__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_9'] = x_get_bus__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_10'] = x_get_bus__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_11'] = x_get_bus__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_12'] = x_get_bus__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_13'] = x_get_bus__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_14'] = x_get_bus__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_15'] = x_get_bus__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_16'] = x_get_bus__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_17'] = x_get_bus__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_18'] = x_get_bus__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_bus__mutmut['x_get_bus__mutmut_19'] = x_get_bus__mutmut_19 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut: MutantDict = {}  # type: ignore


# ── Worker stats endpoint helper ─────────────────────────────────────────────


@_mutmut_mutated(mutants_x_collect_worker_stats__mutmut)
def collect_worker_stats(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_task", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_orig(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_task", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_1(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = None
    for fn in worker_fns:
        task = getattr(fn, "_task", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_2(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = None
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_3(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(None, "_task", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_4(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, None, None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_5(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr("_task", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_6(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_7(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_task", )
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_8(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "XX_taskXX", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_9(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_TASK", None)
        if task:
            stats.append(task.stats)
    return stats


# ── Worker stats endpoint helper ─────────────────────────────────────────────


def x_collect_worker_stats__mutmut_10(worker_fns: list) -> list[dict]:
    """Return circuit-breaker and call stats for all registered workers."""
    stats = []
    for fn in worker_fns:
        task = getattr(fn, "_task", None)
        if task:
            stats.append(None)
    return stats

mutants_x_collect_worker_stats__mutmut['_mutmut_orig'] = x_collect_worker_stats__mutmut_orig # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_1'] = x_collect_worker_stats__mutmut_1 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_2'] = x_collect_worker_stats__mutmut_2 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_3'] = x_collect_worker_stats__mutmut_3 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_4'] = x_collect_worker_stats__mutmut_4 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_5'] = x_collect_worker_stats__mutmut_5 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_6'] = x_collect_worker_stats__mutmut_6 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_7'] = x_collect_worker_stats__mutmut_7 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_8'] = x_collect_worker_stats__mutmut_8 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_9'] = x_collect_worker_stats__mutmut_9 # type: ignore # mutmut generated
mutants_x_collect_worker_stats__mutmut['x_collect_worker_stats__mutmut_10'] = x_collect_worker_stats__mutmut_10 # type: ignore # mutmut generated
