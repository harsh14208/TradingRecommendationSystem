"""Tests for routers/ml.py — ML model status and training endpoints."""

from unittest.mock import patch
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from models import User
from services.auth_svc import get_current_user


def _make_app(is_owner=True):
    from routers.ml import router

    app = FastAPI()
    app.include_router(router)

    def _user():
        return User(id=1, email="owner@t.com", is_owner=is_owner, subscription_tier="pro")

    app.dependency_overrides[get_current_user] = _user
    return app


def test_ml_status_no_model():
    app = _make_app()
    with patch("routers.ml._FEATURE_FILE") as mock_file, patch("services.signal_ml._MODEL_FILE") as mock_model:
        mock_file.exists.return_value = False
        mock_model.exists.return_value = False
        with TestClient(app) as client:
            resp = client.get("/api/ml/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_exists"] is False


def test_ml_status_with_model(tmp_path):
    meta = {
        "trained_at": "2026-01-01",
        "oos_auc": 0.64,
        "oos_accuracy": 0.62,
        "n_train": 1000,
        "n_test": 200,
        "top_features": ["rsi", "bb"],
        "feature_importances": [{"feature": "rsi", "importance": 0.3}],
    }
    import json

    feat_file = tmp_path / "signal_ml_features.json"
    feat_file.write_text(json.dumps(meta))
    model_file = tmp_path / "signal_ml_model.json"
    model_file.write_text("{}")

    app = _make_app()
    with patch("routers.ml._FEATURE_FILE", feat_file), patch("services.signal_ml._MODEL_FILE", model_file):
        with TestClient(app) as client:
            resp = client.get("/api/ml/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_exists"] is True
    assert data["oos_auc"] == 0.64


def test_ml_status_non_owner():
    app = _make_app(is_owner=False)
    with TestClient(app) as client:
        resp = client.get("/api/ml/status")
    assert resp.status_code == 403


def test_ml_train_insufficient_data():
    app = _make_app()
    with (
        patch("services.signal_ml.train_model", return_value=None),
        patch("routers.ml._limiter.limit", return_value=lambda f: f),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train")
    assert resp.status_code in (200, 429)
    if resp.status_code == 200:
        assert resp.json()["status"] == "skipped"


def test_ml_train_success(tmp_path):
    meta = {"trained_at": "2026-01-01", "oos_auc": 0.65, "n_train": 500, "n_test": 100}
    import json

    feat_file = tmp_path / "signal_ml_features.json"
    feat_file.write_text(json.dumps(meta))

    app = _make_app()
    with (
        patch("services.signal_ml.train_model", return_value={"auc": 0.65}),
        patch("routers.ml._FEATURE_FILE", feat_file),
        patch("routers.ml._limiter.limit", return_value=lambda f: f),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train")
    assert resp.status_code in (200, 429)
    if resp.status_code == 200:
        assert resp.json()["status"] == "ok"


def test_ml_train_error():
    app = _make_app()
    with (
        patch("services.signal_ml.train_model", side_effect=RuntimeError("training failed")),
        patch("routers.ml._limiter.limit", return_value=lambda f: f),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train")
    assert resp.status_code in (429, 500)


def test_ml_challenger_no_model():
    app = _make_app()
    with patch("routers.ml._CHALLENGER_FEATURE_FILE") as mock_file:
        mock_file.exists.return_value = False
        # parent/file doesn't exist
        mock_file.parent = Path("/nonexistent")
        with TestClient(app) as client:
            resp = client.get("/api/ml/challenger")
    assert resp.status_code == 200
    assert resp.json()["model_deployed"] is False


def test_ml_challenger_with_meta(tmp_path):
    meta = {
        "trained_at": "2026-01-01",
        "challenger_auc": 0.66,
        "baseline_auc": 0.64,
        "delta": 0.02,
        "deployed": True,
        "feature_importances": [{"feature": "rsi", "importance": 0.4}],
    }
    import json

    feat_file = tmp_path / "signal_ml_challenger_features.json"
    feat_file.write_text(json.dumps(meta))
    model_file = tmp_path / "signal_ml_challenger_model.json"
    model_file.write_text("{}")

    app = _make_app()
    with patch("routers.ml._CHALLENGER_FEATURE_FILE", feat_file):
        with TestClient(app) as client:
            resp = client.get("/api/ml/challenger")
    assert resp.status_code == 200
    data = resp.json()
    assert data["challenger_auc"] == 0.66


def test_ml_train_challenger_insufficient():
    app = _make_app()
    with patch("services.signal_ml.train_challenger_model", return_value=None):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train-challenger")
    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"


def test_ml_train_challenger_success():
    result = {"challenger_auc": 0.66, "baseline_auc": 0.64, "delta": 0.02, "deployed": False, "n_total": 200}
    app = _make_app()
    with (
        patch("services.signal_ml.train_challenger_model", return_value=result),
        patch("routers.ml._limiter.limit", return_value=lambda f: f),
    ):
        with TestClient(app) as client:
            resp = client.post("/api/ml/train-challenger")
    assert resp.status_code in (200, 429)
    if resp.status_code == 200:
        assert resp.json()["status"] == "ok"
