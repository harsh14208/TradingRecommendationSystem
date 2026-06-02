"""
ML management endpoints — owner-only.

GET  /api/ml/status           — model metadata (trained_at, OOS metrics, feature importances)
POST /api/ml/train            — trigger retraining (rate-limited to 1/hour)
POST /api/ml/train-challenger — A17: train 24-feature challenger (structural + raw_score)
GET  /api/ml/challenger       — A17 challenger metadata and interpretation
"""

import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from models import User
from services.auth_svc import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

log = logging.getLogger("signal.ml.router")

_limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/ml", tags=["ml"])

_DATA_DIR = Path(__file__).parent.parent / "data"
_FEATURE_FILE = _DATA_DIR / "signal_ml_features.json"


def _require_owner(user: User = Depends(get_current_user)) -> User:
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")
    return user


def _read_metadata() -> dict:
    """Read persisted model metadata from the features/metadata JSON file."""
    if not _FEATURE_FILE.exists():
        return {}
    try:
        return json.loads(_FEATURE_FILE.read_text())
    except Exception:
        return {}


@router.get("/status")
async def ml_status(owner: User = Depends(_require_owner)):
    """
    Return model metadata if a trained model file exists.

    Response fields:
      trained_at, oos_accuracy, oos_auc, n_train, n_test, top_features,
      feature_importances, model_exists
    """
    from services.signal_ml import _MODEL_FILE

    meta = _read_metadata()
    return {
        "model_exists": _MODEL_FILE.exists(),
        "trained_at": meta.get("trained_at"),
        "oos_accuracy": meta.get("oos_accuracy"),
        "oos_auc": meta.get("oos_auc"),
        "oos_precision": meta.get("oos_precision"),
        "oos_recall": meta.get("oos_recall"),
        "n_train": meta.get("n_train"),
        "n_test": meta.get("n_test"),
        "top_features": meta.get("top_features", []),
        "feature_importances": meta.get("feature_importances", []),
    }


@router.post("/train")
@_limiter.limit("1/hour")
async def ml_train(request: Request, owner: User = Depends(_require_owner)):
    """
    Trigger XGBoost retraining in a background thread.
    Rate-limited to 1 request per hour per IP to prevent abuse.

    Returns the same metadata dict as GET /api/ml/status after training completes.
    """
    log.info(f"[ml] Manual retrain triggered by owner {owner.email}")

    try:
        from services.signal_ml import train_model

        result = await asyncio.to_thread(train_model)
    except Exception as e:
        log.warning(f"[ml] train endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

    if result is None:
        # train_model returns None when there are insufficient samples
        return {
            "status": "skipped",
            "reason": "Insufficient resolved signals (need ≥50 BUY/SELL with outcomes).",
            "model_exists": False,
        }

    # Return fresh metadata from disk (train_model writes it)
    meta = _read_metadata()
    return {
        "status": "ok",
        "model_exists": True,
        "trained_at": meta.get("trained_at"),
        "oos_accuracy": meta.get("oos_accuracy"),
        "oos_auc": meta.get("oos_auc"),
        "oos_precision": meta.get("oos_precision"),
        "oos_recall": meta.get("oos_recall"),
        "n_train": meta.get("n_train"),
        "n_test": meta.get("n_test"),
        "top_features": meta.get("top_features", []),
    }


_CHALLENGER_FEATURE_FILE = Path(__file__).parent.parent / "data" / "signal_ml_challenger_features.json"


def _read_challenger_metadata() -> dict:
    try:
        if _CHALLENGER_FEATURE_FILE.exists():
            return json.loads(_CHALLENGER_FEATURE_FILE.read_text())
    except Exception:
        pass
    return {}


@router.get("/challenger")
async def ml_challenger_status(owner: User = Depends(_require_owner)):
    """A17 challenger metadata — interpretation of whether raw_score adds value."""
    meta = _read_challenger_metadata()
    challenger_file = _CHALLENGER_FEATURE_FILE.parent / "signal_ml_challenger_model.json"
    return {
        "model_deployed": challenger_file.exists(),
        "trained_at": meta.get("trained_at"),
        "challenger_auc": meta.get("challenger_auc"),
        "baseline_auc": meta.get("baseline_auc"),
        "delta": meta.get("delta"),
        "deployed": meta.get("deployed"),
        "training_only": meta.get("training_only"),
        "raw_score_importance_rank": meta.get("raw_score_importance_rank"),
        "interpretation": meta.get("interpretation"),
        "n_total": meta.get("n_total"),
        "top_features": [f["feature"] for f in (meta.get("feature_importances") or [])[:5]],
    }


@router.post("/train-challenger")
@_limiter.limit("1/hour")
async def ml_train_challenger(request: Request, owner: User = Depends(_require_owner)):
    """
    A17: Train the challenger model (23 structural features + raw_score).
    Tests whether the heuristic point accumulator adds discriminating power.
    Rate-limited to 1/hour.
    """
    log.info(f"[ml] A17 challenger train triggered by owner {owner.email}")

    try:
        from services.signal_ml import train_challenger_model

        result = await asyncio.to_thread(train_challenger_model)
    except Exception as e:
        log.warning(f"[ml] A17 challenger train error: {e}")
        raise HTTPException(status_code=500, detail=f"Challenger training failed: {e}")

    if result is None:
        return {
            "status": "skipped",
            "reason": "Insufficient resolved signals (need ≥50) or evaluation failed.",
        }

    return {
        "status": "ok",
        "challenger_auc": result.get("challenger_auc"),
        "baseline_auc": result.get("baseline_auc"),
        "delta": result.get("delta"),
        "deployed": result.get("deployed"),
        "training_only": result.get("training_only"),
        "raw_score_importance_rank": result.get("raw_score_importance_rank"),
        "interpretation": result.get("interpretation"),
        "n_total": result.get("n_total"),
    }
