"""
XGBoost confidence adjustment model.

Trained on resolved signals (outcome_pct not null) from the local DB.
Produces a multiplicative confidence adjustment (0.75–1.25×) that blends
with the deterministic Platt-scaled confidence.

Feature vector: 20 features extracted from the signal dict.
Target: binary win (outcome_pct > 0 for BUY, < 0 for SELL).
Output: adjusted_confidence = base_confidence * clamp(xgb_win_prob / base_win_prob, 0.75, 1.25)
"""
import json
import logging
import math
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger("signal.ml")

_DATA_DIR  = Path(__file__).parent.parent / "data"
_MODEL_FILE   = _DATA_DIR / "signal_ml_model.json"
_FEATURE_FILE = _DATA_DIR / "signal_ml_features.json"
_MAX_CONFIDENCE = 72.0

# Minimum resolved signals before we attempt training
_MIN_SAMPLES = 50
# Temporal train/test split — same philosophy as factor_miner.py
_TRAIN_SPLIT = 0.70

# ── Module-level model cache ───────────────────────────────────────────────────
_model      = None          # cached XGBoost Booster (or None)
_model_mtime: float = 0.0  # mtime of the file when last loaded


# ── Feature extraction ─────────────────────────────────────────────────────────

def _extract_features(sig: dict) -> list[float]:
    """
    Extract the 20-feature vector from a signal dict.
    All values are available at generation time — no look-ahead.
    """
    confidence = float(sig.get("confidence") or 0)
    sentiment  = float(sig.get("sentiment")  or 0)

    sources = sig.get("sources") or []
    if isinstance(sources, str):
        try:
            sources = json.loads(sources)
        except Exception:
            sources = []

    rationale = sig.get("rationale") or []
    if isinstance(rationale, str):
        try:
            rationale = json.loads(rationale)
        except Exception:
            rationale = []

    n_sources   = len(sources)
    n_rationale = len(rationale)
    n_pos = sum(1 for r in rationale if r.get("sentiment") == "pos")
    n_neg = sum(1 for r in rationale if r.get("sentiment") == "neg")

    # rr string → float (e.g. "1:1.5" or "1.5" → 1.5)
    rr_raw = sig.get("rr") or ""
    rr_numeric = 0.0
    try:
        rr_str = str(rr_raw).strip()
        if ":" in rr_str:
            parts = rr_str.split(":")
            rr_numeric = float(parts[-1]) if len(parts) >= 2 else 0.0
        else:
            rr_numeric = float(rr_str) if rr_str else 0.0
    except (ValueError, TypeError):
        rr_numeric = 0.0

    action  = (sig.get("action") or "").upper()
    is_buy  = 1 if action == "BUY" else 0

    has_options      = 1 if "Options"      in sources else 0
    has_dark_pool    = 1 if "Dark Pool"    in sources else 0
    has_fundamentals = 1 if "Fundamentals" in sources else 0
    has_institutional= 1 if "13F"          in sources else 0
    has_macro        = 1 if "Macro"        in sources else 0
    has_earnings     = 1 if "Earnings"     in sources else 0

    session           = (sig.get("session") or "").lower()
    is_pre_market     = 1 if session == "pre" else 0

    style             = (sig.get("style") or "").lower()
    is_position_style = 1 if style == "position" else 0

    entry = sig.get("entry") or 0.0
    stop  = sig.get("stop")  or 0.0
    target= sig.get("target")or 0.0
    price = sig.get("price") or 0.0

    try:
        entry  = float(entry)
        stop   = float(stop)
        target = float(target)
        price  = float(price)
    except (TypeError, ValueError):
        entry = stop = target = price = 0.0

    stop_pct   = abs(entry - stop)   / entry * 100 if entry > 0 and stop   > 0 else 0.0
    target_pct = abs(target - entry) / entry * 100 if entry > 0 and target > 0 else 0.0
    price_log  = math.log10(price) if price > 0 else 0.0

    return [
        confidence,        # 1
        sentiment,         # 2
        n_sources,         # 3
        n_rationale,       # 4
        n_pos,             # 5
        n_neg,             # 6
        rr_numeric,        # 7
        is_buy,            # 8
        has_options,       # 9
        has_dark_pool,     # 10
        has_fundamentals,  # 11
        has_institutional, # 12
        has_macro,         # 13
        has_earnings,      # 14
        is_pre_market,     # 15
        is_position_style, # 16
        stop_pct,          # 17
        target_pct,        # 18
        price_log,         # 19
        # confidence_bin removed: it was a binned duplicate of confidence (feature 1)
        # and was amplifying the high-confidence→low-win-rate inversion by giving
        # the model two correlated channels to overfit on the top confidence band.
    ]


_FEATURE_NAMES = [
    "confidence",
    "sentiment",
    "n_sources",
    "n_rationale",
    "n_pos_rationale",
    "n_neg_rationale",
    "rr_numeric",
    "is_buy",
    "has_options_source",
    "has_dark_pool_source",
    "has_fundamentals_source",
    "has_institutional_source",
    "has_macro_source",
    "has_earnings_source",
    "is_pre_market",
    "is_position_style",
    "stop_pct",
    "target_pct",
    "price_log",
]


# ── Training ──────────────────────────────────────────────────────────────────

def train_model() -> Optional[dict]:
    """
    Train an XGBoost binary classifier on resolved signals from the DB.

    Uses a temporal 70/30 train/test split (oldest 70% for training,
    newest 30% for OOS validation) — same philosophy as factor_miner.py.

    Persists the model to backend/data/signal_ml_model.json and feature
    importances to backend/data/signal_ml_features.json.

    Returns a dict with {oos_accuracy, oos_auc, n_train, n_test, top_features}
    or None if there are insufficient resolved signals.
    """
    try:
        import xgboost as xgb
    except ImportError:
        log.warning("[signal_ml] xgboost not installed — skipping train_model()")
        return None

    try:
        from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
    except ImportError:
        log.warning("[signal_ml] scikit-learn not installed — skipping train_model()")
        return None

    # ── Load resolved signals from DB ─────────────────────────────────────────
    try:
        rows = _load_resolved_signals_sync()
    except Exception as e:
        log.warning(f"[signal_ml] DB read failed: {e}")
        return None

    if len(rows) < _MIN_SAMPLES:
        log.info(
            f"[signal_ml] Only {len(rows)} resolved signals — need {_MIN_SAMPLES} "
            "before training. Skipping."
        )
        return None

    # Sort oldest-first for temporal split
    rows.sort(key=lambda r: r.get("created_at") or "")

    # ── Build feature matrix and target vector ─────────────────────────────────
    X, y = [], []
    for r in rows:
        action      = (r.get("action") or "").upper()
        outcome_pct = r.get("outcome_pct")
        if action not in ("BUY", "SELL") or outcome_pct is None:
            continue
        label = 1 if (action == "BUY" and outcome_pct > 0) or \
                     (action == "SELL" and outcome_pct < 0) else 0
        X.append(_extract_features(r))
        y.append(label)

    if len(X) < _MIN_SAMPLES:
        log.info(f"[signal_ml] After filtering, only {len(X)} usable rows — skipping.")
        return None

    # ── Temporal train/test split ──────────────────────────────────────────────
    split    = max(int(len(X) * _TRAIN_SPLIT), _MIN_SAMPLES)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    if len(X_test) < 5:
        log.info("[signal_ml] Test set too small (< 5 samples) — skipping.")
        return None

    n_train, n_test = len(X_train), len(X_test)
    log.info(f"[signal_ml] Training on {n_train} signals, validating on {n_test}")

    # ── Train XGBoost ──────────────────────────────────────────────────────────
    try:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=3,        # shallower — prevents memorising confidence bands
            learning_rate=0.05, # slower shrinkage with more trees
            min_child_weight=5, # require more samples per leaf
            subsample=0.8,
            colsample_bytree=0.7,
            gamma=0.3,          # min split-loss gain — prunes low-value splits
            reg_alpha=0.1,      # L1: drives weak feature weights to zero
            reg_lambda=2.0,     # L2: shrinks all weights, reduces overfit
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
    except Exception as e:
        log.warning(f"[signal_ml] XGBoost training failed: {e}")
        return None

    # ── OOS evaluation ─────────────────────────────────────────────────────────
    try:
        y_pred      = model.predict(X_test)
        y_prob      = model.predict_proba(X_test)[:, 1]
        oos_acc     = round(float(accuracy_score(y_test, y_pred)),  4)
        oos_prec    = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
        oos_rec     = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
        # roc_auc needs both classes present in y_test; guard gracefully
        if len(set(y_test)) > 1:
            oos_auc = round(float(roc_auc_score(y_test, y_prob)), 4)
        else:
            oos_auc = None
        log.info(
            f"[signal_ml] OOS — accuracy={oos_acc:.3f}  "
            f"precision={oos_prec:.3f}  recall={oos_rec:.3f}  "
            f"AUC={oos_auc}"
        )
    except Exception as e:
        log.warning(f"[signal_ml] Evaluation failed: {e}")
        oos_acc = oos_prec = oos_rec = oos_auc = None

    # ── Feature importances ────────────────────────────────────────────────────
    try:
        importances = model.feature_importances_.tolist()
        fi = sorted(
            [{"feature": n, "importance": round(float(v), 5)}
             for n, v in zip(_FEATURE_NAMES, importances)],
            key=lambda x: -x["importance"],
        )
    except Exception:
        fi = []

    top_features = [f["feature"] for f in fi[:5]]

    # ── Champion / Challenger gate ────────────────────────────────────────────
    # Only deploy the new model if it beats the current champion's OOS AUC.
    # Guards against retraining on a bad sample window replacing a good model.
    _deployed = False
    _champion_auc: Optional[float] = None
    try:
        if _FEATURE_FILE.exists():
            _champ_meta = json.loads(_FEATURE_FILE.read_text())
            _champion_auc = _champ_meta.get("oos_auc")
    except Exception:
        pass

    _should_deploy = (
        oos_auc is None                          # can't compute AUC (too few samples) — deploy anyway
        or _champion_auc is None                  # no existing champion — first run
        or oos_auc > _champion_auc                # challenger beats champion
    )

    if _should_deploy:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            model.get_booster().save_model(str(_MODEL_FILE))
            _deployed = True
            if _champion_auc is None:
                log.info(f"[signal_ml] First model deployed — OOS AUC={oos_auc}")
            else:
                log.info(
                    f"[signal_ml] Challenger deployed — OOS AUC {oos_auc:.4f} > "
                    f"champion {_champion_auc:.4f} (+{oos_auc - _champion_auc:.4f})"
                )
        except Exception as e:
            log.error(f"[signal_ml] WRITE FAILED — {_MODEL_FILE}: {e}")
    else:
        log.warning(
            f"[signal_ml] Challenger rejected — OOS AUC {oos_auc:.4f} <= "
            f"champion {_champion_auc:.4f}. Keeping existing model."
        )

    # ── Persist feature importances + metadata ─────────────────────────────────
    from datetime import datetime as _dt
    metadata = {
        "trained_at":     _dt.utcnow().isoformat(),
        "n_train":        n_train,
        "n_test":         n_test,
        "oos_accuracy":   oos_acc,
        "oos_auc":        oos_auc,
        "oos_precision":  oos_prec,
        "oos_recall":     oos_rec,
        "top_features":   top_features,
        "feature_importances": fi,
        "deployed":       _deployed,
        "champion_auc":   _champion_auc,
    }
    # Always write metadata (so the router can show the last training run even if not deployed)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _FEATURE_FILE.write_text(json.dumps(metadata, indent=2))
        log.info(f"[signal_ml] Metadata saved to {_FEATURE_FILE}")
    except Exception as e:
        log.error(f"[signal_ml] WRITE FAILED — {_FEATURE_FILE}: {e}")

    return {
        "oos_accuracy":  oos_acc,
        "oos_auc":       oos_auc,
        "oos_precision": oos_prec,
        "oos_recall":    oos_rec,
        "n_train":       n_train,
        "n_test":        n_test,
        "top_features":  top_features,
        "deployed":      _deployed,
        "champion_auc":  _champion_auc,
    }


# ── DB access (synchronous, for use inside asyncio.to_thread) ──────────────────

def _load_resolved_signals_sync() -> list[dict]:
    """Load resolved signals via a fresh asyncio event loop (safe inside asyncio.to_thread)."""
    import asyncio as _asyncio
    return _asyncio.run(_load_resolved_signals_async())


async def _load_resolved_signals_async() -> list[dict]:
    """Async DB load using the project's AsyncSessionLocal."""
    from database import AsyncSessionLocal
    from models import Signal
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(
                Signal.ticker,
                Signal.action,
                Signal.confidence,
                Signal.sentiment,
                Signal.sources,
                Signal.rationale,
                Signal.outcome_pct,
                Signal.style,
                Signal.session,
                Signal.rr,
                Signal.entry,
                Signal.stop,
                Signal.target,
                Signal.price,
                Signal.created_at,
            )
            .where(Signal.outcome_pct.isnot(None))
            .where(Signal.action.in_(["BUY", "SELL"]))
            .order_by(Signal.created_at)
        )).all()

    return [
        {
            "ticker":      r.ticker,
            "action":      r.action,
            "confidence":  r.confidence,
            "sentiment":   r.sentiment,
            "sources":     r.sources or [],
            "rationale":   r.rationale or [],
            "outcome_pct": r.outcome_pct,
            "style":       r.style,
            "session":     r.session,
            "rr":          r.rr,
            "entry":       r.entry,
            "stop":        r.stop,
            "target":      r.target,
            "price":       r.price,
            "created_at":  str(r.created_at) if r.created_at else "",
        }
        for r in rows
    ]


# ── Model loading ──────────────────────────────────────────────────────────────

def load_model():
    """
    Load the XGBoost Booster from disk.
    Returns None if the model file does not exist or xgboost is not installed.
    Graceful: the engine works without ML if the file is absent.
    """
    try:
        import xgboost as xgb
    except ImportError:
        return None

    if not _MODEL_FILE.exists():
        return None

    try:
        booster = xgb.Booster()
        booster.load_model(str(_MODEL_FILE))
        return booster
    except Exception as e:
        log.warning(f"[signal_ml] Failed to load model from {_MODEL_FILE}: {e}")
        return None


def get_model():
    """
    Return the cached XGBoost Booster, reloading from disk if the file has
    changed since the last load (lazy, mtime-gated).

    Returns None if the model file does not exist or xgboost is unavailable.
    """
    global _model, _model_mtime

    if not _MODEL_FILE.exists():
        return None

    try:
        current_mtime = _MODEL_FILE.stat().st_mtime
    except OSError:
        return _model

    if _model is None or current_mtime != _model_mtime:
        _model      = load_model()
        _model_mtime = current_mtime if _model is not None else 0.0
        if _model is not None:
            log.info("[signal_ml] Model loaded/reloaded from disk")

    return _model


# ── Confidence adjustment ──────────────────────────────────────────────────────

def adjust_confidence(sig_dict: dict, model) -> float:
    """
    Use the XGBoost model to compute a multiplicative confidence adjustment.

    Adjustment logic:
      win_prob      = model.predict_proba(features)[0][1]
      base_win_prob = sig_dict['confidence'] / 100 * 0.85   (empirical scaling)
      ratio         = clamp(win_prob / max(base_win_prob, 0.01), 0.75, 1.25)
      return        = round(min(72.0, sig_dict['confidence'] * ratio), 1)

    Falls back to the original confidence on any error or if model is None.
    """
    if model is None:
        return sig_dict.get("confidence", 0)

    try:
        import xgboost as xgb
        import numpy as np

        features      = _extract_features(sig_dict)
        feature_array = np.array([features], dtype=float)

        dmatrix   = xgb.DMatrix(feature_array, feature_names=_FEATURE_NAMES)
        win_prob  = float(model.predict(dmatrix)[0])

        base_confidence = float(sig_dict.get("confidence") or 0)
        base_win_prob   = base_confidence / 100.0 * 0.85

        ratio = win_prob / max(base_win_prob, 0.01)
        # Clamp adjustment to ±25%
        ratio = max(0.75, min(1.25, ratio))

        adjusted = round(min(_MAX_CONFIDENCE, base_confidence * ratio), 1)
        return adjusted

    except Exception as e:
        log.debug(f"[signal_ml] adjust_confidence error: {e}")
        return sig_dict.get("confidence", 0)
