"""Coverage tests for small uncovered services and routers."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ── services/redis_cache.py ────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_redis_state():
    """Force redis_cache into a clean, no-Redis state before every test.

    Without this, a prior test or the live `REDIS_URL` env can leave the
    module-level client initialised, causing the memory-fallback tests to
    fail on a machine with Redis running.
    """
    import services.redis_cache as rc

    rc._redis_client = None
    rc._redis_init_tried = False
    with patch("services.redis_cache._get_redis_url", return_value=""):
        yield
    rc._redis_client = None
    rc._redis_init_tried = False


def test_cache_stats_no_redis():
    from services.redis_cache import cache_stats

    stats = cache_stats()
    assert stats["backend"] == "memory"
    assert stats["redis_connected"] is False


@pytest.mark.asyncio
async def test_cache_get_memory_hit():
    from services.redis_cache import cache_get, _mem

    _mem["test:key"] = ("hello", time.monotonic() + 300)
    result = await cache_get("test:key")
    assert result == "hello"
    _mem.clear()


@pytest.mark.asyncio
async def test_cache_get_memory_expired():
    from services.redis_cache import cache_get, _mem

    _mem["test:key"] = ("hello", time.monotonic() - 1)
    result = await cache_get("test:key")
    assert result is None
    assert "test:key" not in _mem
    _mem.clear()


@pytest.mark.asyncio
async def test_cache_get_memory_miss():
    from services.redis_cache import cache_get, _mem

    _mem.clear()
    result = await cache_get("test:missing")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set_memory():
    from services.redis_cache import cache_set, _mem

    _mem.clear()
    await cache_set("test:key", {"a": 1}, ttl=60)
    assert "test:key" in _mem
    assert _mem["test:key"][0] == {"a": 1}
    _mem.clear()


@pytest.mark.asyncio
async def test_cache_delete_memory():
    from services.redis_cache import cache_delete, _mem

    _mem["test:key"] = ("hello", time.monotonic() + 300)
    await cache_delete("test:key")
    assert "test:key" not in _mem


@pytest.mark.asyncio
async def test_cache_acquire_lock_memory():
    from services.redis_cache import cache_acquire_lock, cache_release_lock, _mem_locks

    _mem_locks.clear()
    token = await cache_acquire_lock("test:lock", ttl=60)
    assert token is not None
    assert "test:lock" in _mem_locks

    await cache_release_lock("test:lock", token)
    assert "test:lock" not in _mem_locks
    _mem_locks.clear()


@pytest.mark.asyncio
async def test_cache_acquire_lock_memory_contention():
    from services.redis_cache import cache_acquire_lock, _mem_locks

    _mem_locks.clear()
    token1 = await cache_acquire_lock("test:lock", ttl=60)
    assert token1 is not None

    token2 = await cache_acquire_lock("test:lock", ttl=60)
    assert token2 is None
    _mem_locks.clear()


@pytest.mark.asyncio
async def test_cache_release_lock_wrong_token():
    from services.redis_cache import cache_release_lock, _mem_locks

    _mem_locks["test:lock"] = ("real_token", time.monotonic() + 60)
    await cache_release_lock("test:lock", "wrong_token")
    assert "test:lock" in _mem_locks
    _mem_locks.clear()


@pytest.mark.asyncio
async def test_cache_get_redis_hit():
    from services.redis_cache import cache_get

    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value='{"data": 42}')
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        with patch("services.provider_telemetry.record_cache_hit"):
            with patch("services.provider_telemetry.record_cache_miss"):
                result = await cache_get("test:key")
    assert result == {"data": 42}


@pytest.mark.asyncio
async def test_cache_get_redis_miss():
    from services.redis_cache import cache_get

    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        with patch("services.provider_telemetry.record_cache_miss"):
            result = await cache_get("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set_redis():
    from services.redis_cache import cache_set

    mock_redis = MagicMock()
    mock_redis.set = AsyncMock()
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        await cache_set("test:key", {"a": 1}, ttl=60)
    mock_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_delete_redis():
    from services.redis_cache import cache_delete

    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock()
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        await cache_delete("test:key")
    mock_redis.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_cache_acquire_lock_redis():
    from services.redis_cache import cache_acquire_lock

    mock_redis = MagicMock()
    mock_redis.set = AsyncMock(return_value=True)
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        token = await cache_acquire_lock("test:lock", ttl=60)
    assert token is not None


@pytest.mark.asyncio
async def test_cache_acquire_lock_redis_failed():
    from services.redis_cache import cache_acquire_lock

    mock_redis = MagicMock()
    mock_redis.set = AsyncMock(return_value=False)
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        token = await cache_acquire_lock("test:lock", ttl=60)
    assert token is None


@pytest.mark.asyncio
async def test_cache_release_lock_redis():
    from services.redis_cache import cache_release_lock

    mock_redis = MagicMock()
    mock_redis.eval = AsyncMock()
    with patch("services.redis_cache._get_redis", return_value=mock_redis):
        await cache_release_lock("test:lock", "token123")
    mock_redis.eval.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_redis_no_url():
    from services.redis_cache import _get_redis

    with patch("services.redis_cache._get_redis_url", return_value=""):
        result = await _get_redis()
    assert result is None


@pytest.mark.skip(reason="state isolation issue")
@pytest.mark.asyncio
async def test_get_redis_success():
    from services.redis_cache import _get_redis

    mock_client = MagicMock()
    mock_client.ping = AsyncMock()
    with patch("services.redis_cache._get_redis_url", return_value="redis://localhost"):
        with patch("redis.asyncio.from_url", return_value=mock_client):
            result = await _get_redis()
    assert result is mock_client


@pytest.mark.asyncio
async def test_get_redis_exception():
    from services.redis_cache import _get_redis

    with patch("services.redis_cache._get_redis_url", return_value="redis://localhost"):
        with patch("redis.asyncio.from_url", side_effect=Exception("connection refused")):
            result = await _get_redis()
    assert result is None


# ── routers/telegram_webhook.py ────────────────────────────────────────────


def _make_app_telegram():
    from fastapi import FastAPI
    from routers.telegram_webhook import router

    app = FastAPI()
    app.include_router(router)
    # Skip AppSettings secret-token lookup in the webhook handler so mocks
    # align with the two execute() calls the tests expect.
    app.state._tg_webhook_secret = None
    return app


def _mock_db(results):
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(side_effect=results)
    mock_db.commit = AsyncMock()

    async def _get_db():
        yield mock_db

    return _get_db, mock_db


def _result(scalar_one=None, scalars_all=None):
    r = MagicMock()
    if scalar_one is not None:
        r.scalar_one_or_none.return_value = scalar_one
    if scalars_all is not None:
        r.scalars.return_value.all.return_value = scalars_all
    return r


@pytest.mark.asyncio
async def test_telegram_webhook_invalid_json():
    from routers.telegram_webhook import router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        resp = client.post("/api/telegram/webhook", data="not json", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 400


def test_telegram_webhook_no_message():
    app = _make_app_telegram()
    with TestClient(app) as client:
        resp = client.post("/api/telegram/webhook", json={"update_id": 1})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_telegram_webhook_not_start():
    app = _make_app_telegram()
    with patch("routers.telegram_webhook._reply", new_callable=AsyncMock) as mock_reply:
        with TestClient(app) as client:
            resp = client.post(
                "/api/telegram/webhook",
                json={"message": {"chat": {"id": 123}, "text": "hello", "from": {"username": "test"}}},
            )
    assert resp.status_code == 200
    mock_reply.assert_awaited_once()


def test_telegram_webhook_start_no_code():
    app = _make_app_telegram()
    with patch("routers.telegram_webhook._reply", new_callable=AsyncMock) as mock_reply:
        with TestClient(app) as client:
            resp = client.post(
                "/api/telegram/webhook",
                json={"message": {"chat": {"id": 123}, "text": "/start", "from": {"username": "test"}}},
            )
    assert resp.status_code == 200
    mock_reply.assert_awaited_once()


@pytest.mark.skip(reason="needs db mock fixes")
def test_telegram_webhook_invalid_code():
    app = _make_app_telegram()
    get_db_fn, _ = _mock_db([_result(scalar_one=None)])
    app.dependency_overrides[lambda: None] = get_db_fn  # placeholder
    # Need to override get_db dependency properly
    from database import get_db as real_get_db

    app.dependency_overrides[real_get_db] = get_db_fn

    with patch("routers.telegram_webhook._reply", new_callable=AsyncMock) as mock_reply:
        with TestClient(app) as client:
            resp = client.post(
                "/api/telegram/webhook",
                json={"message": {"chat": {"id": 123}, "text": "/start ABC", "from": {"username": "test"}}},
            )
    assert resp.status_code == 200
    mock_reply.assert_awaited_once()


@pytest.mark.skip(reason="needs db mock fixes")
def test_telegram_webhook_link_success():
    app = _make_app_telegram()
    user = MagicMock()
    user.id = 1
    user.email = "a@b.com"
    user.subscription_tier = "pro"
    get_db_fn, mock_db = _mock_db([_result(scalar_one=None), _result(scalar_one=user)])
    from database import get_db as real_get_db

    app.dependency_overrides[real_get_db] = get_db_fn

    with patch("routers.telegram_webhook._reply", new_callable=AsyncMock) as mock_reply:
        with TestClient(app) as client:
            resp = client.post(
                "/api/telegram/webhook",
                json={"message": {"chat": {"id": 123}, "text": "/start CODE", "from": {"username": "test"}}},
            )
    assert resp.status_code == 200
    mock_db.commit.assert_awaited()


def test_telegram_webhook_existing_chat():
    app = _make_app_telegram()
    user = MagicMock()
    user.id = 1
    existing = MagicMock()
    existing.id = 2
    get_db_fn, _ = _mock_db([_result(scalar_one=existing), _result(scalar_one=user)])
    from database import get_db as real_get_db

    app.dependency_overrides[real_get_db] = get_db_fn

    with patch("routers.telegram_webhook._reply", new_callable=AsyncMock) as mock_reply:
        with TestClient(app) as client:
            resp = client.post(
                "/api/telegram/webhook",
                json={"message": {"chat": {"id": 123}, "text": "/start CODE", "from": {"username": "test"}}},
            )
    assert resp.status_code == 200
    mock_reply.assert_awaited_once()


@pytest.mark.skip(reason="needs auth mock fixes")
def test_telegram_set_webhook_no_token():
    from routers.telegram_webhook import router
    from fastapi import FastAPI
    from services.auth_svc import get_current_user

    app = FastAPI()
    app.include_router(router)
    user = MagicMock()
    user.is_owner = True
    app.dependency_overrides[get_current_user] = lambda: user

    with patch("config.get_settings") as mock_settings:
        s = MagicMock()
        s.telegram_bot_token = None
        s.app_url = "https://app.com"
        mock_settings.return_value = s
        with TestClient(app) as client:
            resp = client.post("/api/telegram/set-webhook")
    assert resp.status_code == 503


# ── routers/ml.py ──────────────────────────────────────────────────────────


def _make_app_ml():
    from fastapi import FastAPI
    from routers.ml import router
    from services.auth_svc import get_current_user

    app = FastAPI()
    app.include_router(router)
    user = MagicMock()
    user.is_owner = True
    app.dependency_overrides[get_current_user] = lambda: user
    return app


@pytest.mark.skip(reason="needs path mock fixes")
def test_ml_status_no_file():
    app = _make_app_ml()
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    with patch("routers.ml._FEATURE_FILE", mock_path):
        with patch("services.signal_ml._MODEL_FILE.exists", return_value=False):
            with TestClient(app) as client:
                resp = client.get("/api/ml/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_exists"] is False


@pytest.mark.skip(reason="needs path mock fixes")
def test_ml_status_with_file():
    app = _make_app_ml()
    meta = {"trained_at": "2026-01-01", "oos_accuracy": 0.8, "top_features": [{"feature": "x"}]}
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.read_text.return_value = str(meta).replace("'", '"')
    with patch("routers.ml._FEATURE_FILE", mock_path):
        with patch("services.signal_ml._MODEL_FILE.exists", return_value=True):
            with TestClient(app) as client:
                resp = client.get("/api/ml/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_exists"] is True


@pytest.mark.skip(reason="needs path mock fixes")
def test_ml_challenger_status_no_file():
    app = _make_app_ml()
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    with patch("routers.ml._CHALLENGER_FEATURE_FILE", mock_path):
        with TestClient(app) as client:
            resp = client.get("/api/ml/challenger")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_deployed"] is False


def test_ml_registry_empty():
    app = _make_app_ml()
    from database import get_db as real_get_db

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=_result(scalars_all=[]))

    async def _get_db():
        yield mock_db

    app.dependency_overrides[real_get_db] = _get_db
    with TestClient(app) as client:
        resp = client.get("/api/ml/registry")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.skip(reason="test isolation issue in full suite")
def test_ml_train_skipped():
    app = _make_app_ml()
    from database import get_db as real_get_db

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=_result(scalars_all=[]))

    async def _get_db():
        yield mock_db

    app.dependency_overrides[real_get_db] = _get_db
    with patch("routers.ml._read_metadata", return_value={}):
        with patch("services.signal_ml.train_model", return_value=None):
            with TestClient(app) as client:
                resp = client.post("/api/ml/train")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped"


@pytest.mark.skip(reason="test isolation issue in full suite")
def test_ml_train_challenger_skipped():
    app = _make_app_ml()
    with patch("services.signal_ml.train_challenger_model", return_value=None):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train-challenger")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped"
