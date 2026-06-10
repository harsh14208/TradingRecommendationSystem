"""TSYS-7a (model registry), 7d (calibration rollback), 9c (broker parity)."""

import json
import types
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from models import User
from services.auth_svc import get_current_user


# ── TSYS-7a model registry ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_model_registry_writes_artifact():
    from routers.ml import _record_model_registry

    db = AsyncMock()
    db.get = AsyncMock(return_value=None)  # not already registered
    db.add = MagicMock()
    db.commit = AsyncMock()

    meta = {
        "trained_at": "2026-06-08T00:00:00",
        "features": ["rsi", "bb"],
        "n_train": 300,
        "n_test": 60,
        "oos_auc": 0.64,
    }
    await _record_model_registry(db, meta, kind="entry")

    db.add.assert_called_once()
    row = db.add.call_args[0][0]
    assert row.model_id == "entry-2026-06-08T00:00:00"
    assert len(row.feature_schema_hash) == 64
    assert row.metrics["oos_auc"] == 0.64
    assert row.is_active is False  # registered, not auto-deployed


@pytest.mark.asyncio
async def test_record_model_registry_idempotent_on_existing():
    from routers.ml import _record_model_registry

    db = AsyncMock()
    db.get = AsyncMock(return_value=object())  # already exists
    db.add = MagicMock()
    await _record_model_registry(db, {"trained_at": "x", "features": []})
    db.add.assert_not_called()


# ── TSYS-7d calibration rollback ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_archive_current_calibration(monkeypatch):
    from services import calibration

    monkeypatch.setattr(calibration, "load_calibration", lambda: {"last_run": "2026-06-08T00:00:00", "x": 1})
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    db.add = MagicMock()
    db.commit = AsyncMock()

    version = await calibration.archive_current_calibration(db)
    assert version == "2026-06-08T00:00:00"
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_restore_calibration_version(monkeypatch, tmp_path):
    from services import calibration

    cal_file = tmp_path / "calibration.json"
    monkeypatch.setattr(calibration, "_CAL_FILE", cal_file)
    monkeypatch.setattr(calibration, "_DATA_DIR", tmp_path)

    row = types.SimpleNamespace(calibration_data={"restored": True}, is_active=False)
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: row))
    db.commit = AsyncMock()

    ok = await calibration.restore_calibration_version(db, "v1")
    assert ok is True
    assert json.loads(cal_file.read_text()) == {"restored": True}
    assert row.is_active is True


@pytest.mark.asyncio
async def test_restore_calibration_missing_version(monkeypatch):
    from services import calibration

    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    assert await calibration.restore_calibration_version(db, "nope") is False


# ── TSYS-9c broker parity ────────────────────────────────────────────────────


def test_broker_parity_flags_divergence():
    from routers.broker import router

    user = User(id=1, email="t@t.com", subscription_tier="pro", subscription_status="active")
    user.alpaca_key_enc = None  # no creds → positions unavailable, no broker call
    user.alpaca_secret_enc = None
    user.alpaca_account_type = "paper"
    user.auto_execute_broker = "alpaca"

    orders = [
        types.SimpleNamespace(
            id=1,
            signal_id=1,
            symbol="NVDA",
            side="buy",
            notional=100.0,
            alpaca_order_id="o1",
            status="filled",
            error_msg=None,
            created_at=None,
        ),
        types.SimpleNamespace(
            id=2,
            signal_id=2,
            symbol="AAPL",
            side="buy",
            notional=50.0,
            alpaca_order_id=None,
            status="orphan",
            error_msg="x",
            created_at=None,
        ),
    ]
    db = MagicMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=lambda: MagicMock(all=lambda: orders)))

    async def _get_db():
        yield db

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = _get_db

    resp = TestClient(app).get("/api/me/broker/parity")
    assert resp.status_code == 200
    data = resp.json()
    assert data["positions_available"] is False
    assert data["diverged_count"] == 1  # the orphan
    assert data["orders"][0]["filled"] is True
    assert data["orders"][1]["diverged"] == "orphan"
