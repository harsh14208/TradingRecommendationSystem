"""
Tests for services/worker_bus.py:
  - WorkerBus (asyncio.Queue backend)
  - get_bus() singleton
  - collect_worker_stats()

No Redis is used — all tests run against the default asyncio.Queue backend.
"""
import sys
import os
import asyncio
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.worker_bus import (
    WorkerBus,
    ScoringResult,
    WorkerTask,
    CircuitBreaker,
    get_bus,
    collect_worker_stats,
)


# ── WorkerBus asyncio.Queue backend ──────────────────────────────────────────

class TestWorkerBusAsyncioBackend:

    @pytest.mark.asyncio
    async def test_publish_and_consume(self):
        """Published payload can be consumed from the same stream."""
        bus = WorkerBus()
        payload = {"ticker": "AAPL", "score": 42}
        await bus.publish("test_stream", payload)

        received = []
        async for item in bus.consume("test_stream", timeout=1.0):
            received.append(item)

        assert received == [payload]

    @pytest.mark.asyncio
    async def test_consume_empty_stream_returns_nothing(self):
        """Consuming from a stream that was never published to returns nothing."""
        bus = WorkerBus()
        received = []
        async for item in bus.consume("nonexistent_stream", timeout=0.05):
            received.append(item)
        assert received == []

    @pytest.mark.asyncio
    async def test_consume_timeout_on_empty_queue(self):
        """Consuming from a queue that has been created but nothing published times out."""
        bus = WorkerBus()
        # Create the queue by publishing and then draining it
        await bus.publish("drain_me", {"x": 1})
        async for _ in bus.consume("drain_me", timeout=0.1):
            pass
        # Now queue is empty — consume should time out without error
        received = []
        async for item in bus.consume("drain_me", timeout=0.05):
            received.append(item)
        assert received == []

    @pytest.mark.asyncio
    async def test_publish_creates_queue_for_new_stream(self):
        """Publishing to a new stream auto-creates its Queue."""
        bus = WorkerBus()
        assert "brand_new" not in bus._queues
        await bus.publish("brand_new", {"v": 1})
        assert "brand_new" in bus._queues

    @pytest.mark.asyncio
    async def test_multiple_publishes_fifo_order(self):
        """Multiple payloads are consumed in FIFO order."""
        bus = WorkerBus()
        for i in range(3):
            await bus.publish("fifo_stream", {"i": i})

        results = []
        for _ in range(3):
            async for item in bus.consume("fifo_stream", timeout=0.5):
                results.append(item["i"])

        assert results == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_close_no_redis_is_noop(self):
        """close() on a bus without Redis is a no-op (no exception)."""
        bus = WorkerBus()
        await bus.close()  # Should not raise


# ── get_bus singleton ─────────────────────────────────────────────────────────

class TestGetBus:

    def test_returns_worker_bus_instance(self):
        from services import worker_bus as wb_module
        # Reset singleton so we get a clean state
        wb_module._bus = None
        bus = get_bus()
        assert isinstance(bus, WorkerBus)

    def test_returns_same_instance_on_repeated_calls(self):
        from services import worker_bus as wb_module
        wb_module._bus = None
        bus1 = get_bus()
        bus2 = get_bus()
        assert bus1 is bus2

    def test_singleton_reset_gives_fresh_instance(self):
        from services import worker_bus as wb_module
        wb_module._bus = None
        bus1 = get_bus()
        wb_module._bus = None
        bus2 = get_bus()
        assert bus1 is not bus2


# ── collect_worker_stats ──────────────────────────────────────────────────────

class TestCollectWorkerStats:

    def test_empty_list_returns_empty(self):
        result = collect_worker_stats([])
        assert result == []

    def test_function_without_task_attr_is_skipped(self):
        def plain_fn(): pass
        result = collect_worker_stats([plain_fn])
        assert result == []

    def test_worker_task_stats_included(self):
        @WorkerTask(name="stat_test_w", timeout=5.0, retries=1)
        async def my_worker():
            return ScoringResult()

        stats = collect_worker_stats([my_worker])
        assert len(stats) == 1
        assert stats[0]["name"] == "stat_test_w"

    def test_stats_contain_expected_keys(self):
        @WorkerTask(name="keys_w", timeout=5.0, retries=1)
        async def keys_worker():
            return ScoringResult()

        stats = collect_worker_stats([keys_worker])
        s = stats[0]
        assert "calls" in s
        assert "errors" in s
        assert "error_rate" in s
        assert "circuit_open" in s

    def test_multiple_workers_all_included(self):
        @WorkerTask(name="w1", timeout=5.0, retries=1)
        async def worker_one():
            return ScoringResult()

        @WorkerTask(name="w2", timeout=5.0, retries=1)
        async def worker_two():
            return ScoringResult()

        stats = collect_worker_stats([worker_one, worker_two])
        assert len(stats) == 2
        names = {s["name"] for s in stats}
        assert names == {"w1", "w2"}


# ── WorkerTask retry logic ─────────────────────────────────────────────────────

class TestWorkerTaskRetries:

    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self):
        """Worker fails once then succeeds — should return ok=True."""
        call_count = 0

        @WorkerTask(name="retry_w", timeout=5.0, retries=2)
        async def retry_worker():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("first try failed")
            return ScoringResult(score=7.0)

        result = await retry_worker()
        assert result.ok is True
        assert result.score == 7.0
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_returns_ok_false(self):
        """Worker fails every attempt — should return ok=False."""
        @WorkerTask(name="always_fail_w", timeout=5.0, retries=2)
        async def always_fail():
            raise RuntimeError("always fails")

        result = await always_fail()
        assert result.ok is False

    @pytest.mark.asyncio
    async def test_non_scoring_result_return_becomes_empty(self):
        """Worker returning non-ScoringResult is wrapped in empty ScoringResult."""
        @WorkerTask(name="raw_ret_w", timeout=5.0, retries=1)
        async def raw_return():
            return {"not": "a ScoringResult"}

        result = await raw_return()
        # WorkerTask wraps non-ScoringResult in ScoringResult()
        assert isinstance(result, ScoringResult)
        assert result.score == 0.0
