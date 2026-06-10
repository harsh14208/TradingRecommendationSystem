import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models import BackgroundJobRun, ProviderTelemetry
from services.provider_telemetry import (
    current_cycle_id,
    init_cycle_telemetry,
    record_api_call,
    record_cache_hit,
    record_cache_miss,
    update_quota,
    flush_cycle_telemetry,
)


@pytest.mark.asyncio
async def test_contextvar_task_isolation():
    """Verify that current_cycle_id ContextVar isolates values between concurrent tasks."""
    assert current_cycle_id.get() is None

    async def task_a():
        token = current_cycle_id.set("cycle-A")
        await asyncio.sleep(0.05)
        assert current_cycle_id.get() == "cycle-A"
        current_cycle_id.reset(token)

    async def task_b():
        token = current_cycle_id.set("cycle-B")
        await asyncio.sleep(0.02)
        assert current_cycle_id.get() == "cycle-B"
        current_cycle_id.reset(token)

    await asyncio.gather(task_a(), task_b())
    assert current_cycle_id.get() is None


def test_telemetry_recording():
    """Verify in-memory telemetry records and quota updates."""
    cycle_id = "test-cycle-123"
    init_cycle_telemetry(cycle_id)

    record_api_call(cycle_id, "polygon", throttled=True)
    record_api_call(cycle_id, "polygon", fallback=True)
    record_cache_hit(cycle_id, "polygon")
    record_cache_miss(cycle_id, "polygon")
    update_quota(cycle_id, "polygon", 4999)

    from services.provider_telemetry import _telemetry_store

    stats = _telemetry_store[cycle_id]["polygon"]
    assert stats["api_calls"] == 2
    assert stats["throttles"] == 1
    assert stats["fallback_usage"] == 1
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 1
    assert stats["quota_remaining"] == 4999


@pytest.mark.asyncio
async def test_flush_cycle_telemetry():
    """Verify that flush_cycle_telemetry correctly writes memory telemetry to the DB."""
    cycle_id = "flush-cycle-99"
    init_cycle_telemetry(cycle_id)
    record_api_call(cycle_id, "alpaca")

    # Mock DB write context manager
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_db = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_db.return_value.__aexit__.return_value = None

    with patch("services.provider_telemetry.AsyncSessionLocal", mock_db):
        await flush_cycle_telemetry(cycle_id)

        # Should add a ProviderTelemetry record
        mock_session.add.assert_called_once()
        added_telemetry = mock_session.add.call_args[0][0]
        assert isinstance(added_telemetry, ProviderTelemetry)
        assert added_telemetry.cycle_id == cycle_id
        assert added_telemetry.provider == "alpaca"
        assert added_telemetry.api_calls == 1

        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_supervise_job_logging_success():
    """Verify that _supervise wrapper runs coro and logs run to the database."""
    from main import _supervise

    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_run = MagicMock()
    mock_run.id = 777

    def mock_add(x):
        x.id = 777

    mock_session.add.side_effect = mock_add
    mock_session.get = AsyncMock(return_value=mock_run)

    mock_db = MagicMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_db.return_value.__aexit__.return_value = None

    async def sample_coro():
        await asyncio.sleep(0.01)

    with (
        patch("database.AsyncSessionLocal", mock_db),
        patch("services.redis_cache.cache_acquire_lock", return_value="token123"),
        patch("services.redis_cache.cache_release_lock", return_value=None),
    ):
        task = _supervise("weekly_ml_retrain", sample_coro, restart=False)
        await task

        # Check DB calls for job run
        assert mock_session.add.called
        run_record = mock_session.add.call_args[0][0]
        assert isinstance(run_record, BackgroundJobRun)
        assert run_record.job_name == "weekly_ml_retrain"

        # Commit called for start and end
        assert mock_session.commit.call_count == 2
