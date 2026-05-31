"""
XGBoost confidence adjustment — two complementary models.

Signal model  (live DB):   learns from signal metadata (sources, rationale, style).
Entry model   (backtest):  learns from technical setup at entry (BB%B, IBS, VWAP%,
                           RSI, ADX, VIX…) trained on 23yr × 74-ticker backtest.

At inference both win-probs are blended (50/50) then applied as a single
multiplicative adjustment (0.75–1.25×) to the deterministic Platt-scaled confidence.

Signal model feature vector : 23 raw structural features from signal dict.
  NOTE: `confidence` and `sentiment` (Platt-scaled heuristic outputs) are
  intentionally excluded — feeding the scoring function's own output back into
  XGBoost as a feature creates a circular dependency: the model learns a
  tautological "high confidence → high win rate" relationship and conflates
  alpha quality with portfolio-risk haircuts already baked into the score.
  The 23 remaining features are all independent signals available at generation time.
Entry model feature vector  : 14 raw features from tech dict + VIX + sector.
Target (both models)        : binary win (net_pct > 0 for BUY, < 0 for SELL).
"""

import json
import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Optional

log = logging.getLogger("signal.ml")

_DATA_DIR = Path(__file__).parent.parent / "data"
_MODEL_FILE = _DATA_DIR / "signal_ml_model.json"
_FEATURE_FILE = _DATA_DIR / "signal_ml_features.json"
_ENTRY_MODEL_FILE = _DATA_DIR / "backtest_ml_model.json"
_ENTRY_FEATURE_FILE = _DATA_DIR / "backtest_ml_features.json"
_MAX_CONFIDENCE = 72.0

# Minimum resolved signals before we attempt training
_MIN_SAMPLES = 50
# Temporal train/test split — same philosophy as factor_miner.py
_TRAIN_SPLIT = 0.70

# ── Module-level model caches ─────────────────────────────────────────────────
_model = None  # signal model (live DB)
_model_mtime: float = 0.0
_entry_model = None  # entry model (backtest)
_entry_model_mtime: float = 0.0


# ── Feature helpers ───────────────────────────────────────────────────────────

_SECTOR_ORD: dict[str, int] = {
    "XLK": 0,
    "XLY": 1,
    "XLC": 2,
    "XLF": 3,
    "XLB": 4,
    "XLI": 5,
    "XLV": 6,
    "XLE": 7,
    "XLP": 8,
    "XLRE": 9,
    "XLU": 10,
}


def _sector_ord(sector: str | None) -> float:
    """Sector ETF → ordinal int; -1 (NaN proxy) when missing."""
    if not sector:
        return float("nan")
    return float(_SECTOR_ORD.get(sector.upper(), -1))


def _dte_bucket(dte: int | None) -> float:
    """
    Days-to-earnings → bucket int; NaN when missing.
    0 = <7d (blackout zone)
    1 = 7–34d (approaching earnings)
    2 = 35–65d (post-earnings exhaustion — −24.8pp WR in backtest §53)
    3 = >65d (clean, far from earnings)
    """
    if dte is None:
        return float("nan")
    if dte < 7:
        return 0.0
    if dte < 35:
        return 1.0
    if dte <= 65:
        return 2.0
    return 3.0


# ── Feature extraction ─────────────────────────────────────────────────────────


def _extract_features(sig: dict) -> list[float]:
    """
    Extract the 23-feature structural vector from a signal dict.
    All values are available at generation time — no look-ahead.
    `confidence` and `sentiment` are intentionally absent: they are Platt-scaled
    outputs of the heuristic scoring function, and including them would create a
    circular dependency (the ML model would learn from its own input signal).
    Sparse fields (sector, dte, rs_vs_sector) use NaN when absent;
    XGBoost handles NaN natively via its missing-value split logic.
    """
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

    n_sources = len(sources)
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

    action = (sig.get("action") or "").upper()
    is_buy = 1 if action == "BUY" else 0

    has_options = 1 if "Options" in sources else 0
    has_dark_pool = 1 if "Dark Pool" in sources else 0
    has_fundamentals = 1 if "Fundamentals" in sources else 0
    has_institutional = 1 if "13F" in sources else 0
    has_macro = 1 if "Macro" in sources else 0
    has_earnings = 1 if "Earnings" in sources else 0

    session = (sig.get("session") or "").lower()
    is_pre_market = 1 if session == "pre" else 0

    style = (sig.get("style") or "").lower()
    is_position_style = 1 if style == "position" else 0

    entry = sig.get("entry") or 0.0
    stop = sig.get("stop") or 0.0
    target = sig.get("target") or 0.0
    price = sig.get("price") or 0.0

    try:
        entry = float(entry)
        stop = float(stop)
        target = float(target)
        price = float(price)
    except (TypeError, ValueError):
        entry = stop = target = price = 0.0

    stop_pct = abs(entry - stop) / entry * 100 if entry > 0 and stop > 0 else 0.0
    target_pct = abs(target - entry) / entry * 100 if entry > 0 and target > 0 else 0.0
    price_log = math.log10(price) if price > 0 else 0.0

    # ── Calendar features (proven in backtest: 38pp DOW WR gap, Sep/Oct effect) ─
    try:
        dt = datetime.fromisoformat(str(sig.get("created_at") or ""))
        dow = float(dt.weekday())  # 0=Mon … 4=Fri
        month = float(dt.month)  # 1–12
    except (ValueError, TypeError):
        dow = float("nan")
        month = float("nan")

    # ── Price-action context (100% populated) ────────────────────────────────────
    change_pct = float(sig.get("change_pct") or 0.0)

    # ── Sparse context features (NaN when absent; XGBoost handles natively) ──────
    sector_ord = _sector_ord(sig.get("sector_etf"))
    dte_bucket = _dte_bucket(sig.get("days_to_earnings"))
    rs_vs_sector = float(sig.get("rs_vs_sector") or 0.0) if sig.get("rs_vs_sector") is not None else float("nan")
    # raw_score: pre-heuristic alpha score from _assemble_signal().  NaN for
    # historical rows (pre-migration) — XGBoost splits on presence/absence natively.
    _rs = sig.get("raw_score")
    raw_score = float(_rs) if _rs is not None else float("nan")

    return [
        n_sources,  # 1
        n_rationale,  # 2
        n_pos,  # 3
        n_neg,  # 4
        rr_numeric,  # 5
        is_buy,  # 6
        has_options,  # 7
        has_dark_pool,  # 8
        has_fundamentals,  # 9
        has_institutional,  # 10
        has_macro,  # 11
        has_earnings,  # 12
        is_pre_market,  # 13
        is_position_style,  # 14
        stop_pct,  # 15
        target_pct,  # 16
        price_log,  # 17
        change_pct,  # 18 — day's price move at signal time; MR fires on down days
        dow,  # 19 — day of week; Mon 79.4% WR vs Thu 41.2% (backtest §5b)
        month,  # 20 — Sep/Oct seasonality (-5pp gate already in delivery_gates)
        sector_ord,  # 21 — sector ETF ordinal; NaN when absent (~82% sparse)
        dte_bucket,  # 22 — earnings proximity bucket; post-earn window −24.8pp WR
        rs_vs_sector,  # 23 — relative strength vs sector; NaN when absent (~82% sparse)
        raw_score,  # 24 — raw alpha score (NaN for pre-migration rows)
    ]


_FEATURE_NAMES = [
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
    "change_pct",
    "day_of_week",
    "month",
    "sector_ord",
    "dte_bucket",
    "rs_vs_sector",
    "raw_score",
]


# ── Entry model — technical features ─────────────────────────────────────────
# 14 features, all derivable from the live `tech` dict + VIX + sector + datetime.

_ENTRY_FEATURE_NAMES = [
    "bb_pct_b",  # Bollinger Band %B (0=lower band, 1=upper)
    "ibs",  # Intraday Bar Score (0=bottom of bar range, 1=top)
    "vwap_pct",  # % deviation from 20d VWAP (negative = oversold)
    "rsi",  # RSI(14)
    "adx",  # ADX(14) trend strength
    "rvol",  # Relative volume vs 20d avg
    "atr_pct",  # ATR as % of price
    "price_zscore",  # Price z-score (20d rolling)
    "ou_halflife",  # OU mean-reversion half-life (days)
    "hurst",  # Hurst exponent (<0.5 = mean-reverting)
    "vix",  # VIX level (macro regime)
    "sector_ord",  # Sector ETF ordinal (XLK=0 … XLU=10)
    "dow",  # Day of week (0=Mon … 4=Fri)
    "month",  # Month (1–12)
]


def _extract_entry_features(
    tech: dict,
    vix: float | None,
    sector_etf: str | None,
    dow: int | None,
    month: int | None,
) -> list[float]:
    """
    Extract the 14-feature entry vector from the live tech dict.
    All values are available at signal-generation time — no look-ahead.
    Missing fields return NaN; XGBoost handles NaN via its missing-value split.
    """

    def _f(key: str) -> float:
        v = tech.get(key)
        if v is None:
            return float("nan")
        try:
            f = float(v)
            return float("nan") if math.isnan(f) else f
        except (TypeError, ValueError):
            return float("nan")

    price = tech.get("price") or 0.0
    atr = tech.get("atr") or 0.0
    try:
        atr_pct = float(atr) / float(price) * 100.0 if float(price) > 0 else float("nan")
    except (TypeError, ValueError):
        atr_pct = float("nan")

    return [
        _f("bb_pct_b"),
        _f("ibs"),
        _f("vwap_pct"),
        _f("rsi"),
        _f("adx"),
        _f("rvol"),
        atr_pct,
        _f("price_zscore"),
        _f("ou_halflife"),
        _f("hurst"),
        float(vix) if vix is not None else float("nan"),
        _sector_ord(sector_etf),
        float(dow) if dow is not None else float("nan"),
        float(month) if month is not None else float("nan"),
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
        log.info(f"[signal_ml] Only {len(rows)} resolved signals — need {_MIN_SAMPLES} before training. Skipping.")
        return None

    # Sort oldest-first for temporal split
    rows.sort(key=lambda r: r.get("created_at") or "")

    # ── Build feature matrix and target vector ─────────────────────────────────
    X, y = [], []
    for r in rows:
        action = (r.get("action") or "").upper()
        outcome_pct = r.get("outcome_pct")
        if action not in ("BUY", "SELL") or outcome_pct is None:
            continue
        label = 1 if (action == "BUY" and outcome_pct > 0) or (action == "SELL" and outcome_pct < 0) else 0
        X.append(_extract_features(r))
        y.append(label)

    if len(X) < _MIN_SAMPLES:
        log.info(f"[signal_ml] After filtering, only {len(X)} usable rows — skipping.")
        return None

    # ── Temporal train/test split ──────────────────────────────────────────────
    split = max(int(len(X) * _TRAIN_SPLIT), _MIN_SAMPLES)
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
            max_depth=3,  # shallower — prevents memorising confidence bands
            learning_rate=0.05,  # slower shrinkage with more trees
            min_child_weight=5,  # require more samples per leaf
            subsample=0.8,
            colsample_bytree=0.7,
            gamma=0.3,  # min split-loss gain — prunes low-value splits
            reg_alpha=0.1,  # L1: drives weak feature weights to zero
            reg_lambda=2.0,  # L2: shrinks all weights, reduces overfit
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
    except Exception as e:
        log.warning(f"[signal_ml] XGBoost training failed: {e}")
        return None

    # ── OOS evaluation ─────────────────────────────────────────────────────────
    try:
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        oos_acc = round(float(accuracy_score(y_test, y_pred)), 4)
        oos_prec = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
        oos_rec = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
        # roc_auc needs both classes present in y_test; guard gracefully
        if len(set(y_test)) > 1:
            oos_auc = round(float(roc_auc_score(y_test, y_prob)), 4)
        else:
            oos_auc = None
        log.info(
            f"[signal_ml] OOS — accuracy={oos_acc:.3f}  precision={oos_prec:.3f}  recall={oos_rec:.3f}  AUC={oos_auc}"
        )
    except Exception as e:
        log.warning(f"[signal_ml] Evaluation failed: {e}")
        oos_acc = oos_prec = oos_rec = oos_auc = None

    # ── Feature importances ────────────────────────────────────────────────────
    try:
        importances = model.feature_importances_.tolist()
        fi = sorted(
            [{"feature": n, "importance": round(float(v), 5)} for n, v in zip(_FEATURE_NAMES, importances)],
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
        oos_auc is None  # can't compute AUC (too few samples) — deploy anyway
        or _champion_auc is None  # no existing champion — first run
        or oos_auc > _champion_auc  # challenger beats champion
    )

    if _should_deploy:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            model.get_booster().save_model(str(_MODEL_FILE))
            _deployed = True
            if _champion_auc is None or oos_auc is None:
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
        "trained_at": _dt.utcnow().isoformat(),
        "n_train": n_train,
        "n_test": n_test,
        "oos_accuracy": oos_acc,
        "oos_auc": oos_auc,
        "oos_precision": oos_prec,
        "oos_recall": oos_rec,
        "top_features": top_features,
        "feature_importances": fi,
        "deployed": _deployed,
        "champion_auc": _champion_auc,
    }
    # Always write metadata (so the router can show the last training run even if not deployed)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _FEATURE_FILE.write_text(json.dumps(metadata, indent=2))
        log.info(f"[signal_ml] Metadata saved to {_FEATURE_FILE}")
    except Exception as e:
        log.error(f"[signal_ml] WRITE FAILED — {_FEATURE_FILE}: {e}")

    return {
        "oos_accuracy": oos_acc,
        "oos_auc": oos_auc,
        "oos_precision": oos_prec,
        "oos_recall": oos_rec,
        "n_train": n_train,
        "n_test": n_test,
        "top_features": top_features,
        "deployed": _deployed,
        "champion_auc": _champion_auc,
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
        rows = (
            await db.execute(
                select(
                    Signal.ticker,
                    Signal.action,
                    Signal.confidence,
                    Signal.raw_score,
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
                    Signal.change_pct,
                    Signal.days_to_earnings,
                    Signal.sector_etf,
                    Signal.rs_vs_sector,
                )
                .where(Signal.outcome_pct.isnot(None))
                .where(Signal.action.in_(["BUY", "SELL"]))
                .order_by(Signal.created_at)
            )
        ).all()

    return [
        {
            "ticker": r.ticker,
            "action": r.action,
            "confidence": r.confidence,
            "raw_score": r.raw_score,
            "sentiment": r.sentiment,
            "sources": r.sources or [],
            "rationale": r.rationale or [],
            "outcome_pct": r.outcome_pct,
            "style": r.style,
            "session": r.session,
            "rr": r.rr,
            "entry": r.entry,
            "stop": r.stop,
            "target": r.target,
            "price": r.price,
            "created_at": str(r.created_at) if r.created_at else "",
            "change_pct": r.change_pct,
            "days_to_earnings": r.days_to_earnings,
            "sector_etf": r.sector_etf,
            "rs_vs_sector": r.rs_vs_sector,
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
        _model = load_model()
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
        import numpy as np
        import xgboost as xgb

        features = _extract_features(sig_dict)
        feature_array = np.array([features], dtype=float)

        dmatrix = xgb.DMatrix(feature_array, feature_names=_FEATURE_NAMES)
        win_prob = float(model.predict(dmatrix)[0])

        base_confidence = float(sig_dict.get("confidence") or 0)
        base_win_prob = base_confidence / 100.0 * 0.85

        ratio = win_prob / max(base_win_prob, 0.01)
        # Clamp adjustment to ±25%
        ratio = max(0.75, min(1.25, ratio))

        adjusted = round(min(_MAX_CONFIDENCE, base_confidence * ratio), 1)
        return adjusted

    except Exception as e:
        log.debug(f"[signal_ml] adjust_confidence error: {e}")
        return sig_dict.get("confidence", 0)


# ── Entry model — loader + inference ─────────────────────────────────────────


def get_entry_model():
    """
    Return the cached backtest entry model, reloading on file change.
    Returns None when the file is absent or xgboost is unavailable.
    """
    global _entry_model, _entry_model_mtime

    if not _ENTRY_MODEL_FILE.exists():
        return None

    try:
        current_mtime = _ENTRY_MODEL_FILE.stat().st_mtime
    except OSError:
        return _entry_model

    if _entry_model is None or current_mtime != _entry_model_mtime:
        try:
            import xgboost as xgb

            b = xgb.Booster()
            b.load_model(str(_ENTRY_MODEL_FILE))
            _entry_model = b
            _entry_model_mtime = current_mtime
            log.info("[signal_ml] Entry model loaded/reloaded from disk")
        except Exception as e:
            log.warning(f"[signal_ml] Failed to load entry model: {e}")
            _entry_model = None

    return _entry_model


# ── Sector-specific entry model cache ─────────────────────────────────────────
# Keyed by sector ETF (e.g. "XLF"). Values are (booster, mtime) pairs.
# Populated lazily by get_sector_entry_model().
_sector_models: dict[str, tuple] = {}


def get_sector_entry_model(sector_etf: str | None):
    """Return the sector-specific backtest entry model, or None if unavailable.

    Sector models are trained by train_backtest_ml.py and saved as
    `backtest_ml_model_{SECTOR}.json`. They are preferred over the global model
    for their respective sectors because they are calibrated on sector-specific
    technical dynamics (XLF rate-sensitivity, XLU utility cycles, etc.).

    Falls back gracefully: returns None when the sector file doesn't exist.
    """
    if not sector_etf:
        return None
    key = sector_etf.upper()
    model_file = _DATA_DIR / f"backtest_ml_model_{key}.json"
    if not model_file.exists():
        return None

    try:
        current_mtime = model_file.stat().st_mtime
    except OSError:
        return _sector_models.get(key, (None, 0))[0]

    cached_model, cached_mtime = _sector_models.get(key, (None, 0.0))
    if cached_model is None or current_mtime != cached_mtime:
        try:
            import xgboost as xgb

            b = xgb.Booster()
            b.load_model(str(model_file))
            _sector_models[key] = (b, current_mtime)
            log.info(f"[signal_ml] Sector model loaded: {key}")
            return b
        except Exception as e:
            log.warning(f"[signal_ml] Failed to load sector model {key}: {e}")
            _sector_models[key] = (None, 0.0)
            return None
    return cached_model


def predict_entry_prob_sector(
    tech: dict,
    vix: float | None,
    sector_etf: str | None,
) -> "float | None":
    """Use the sector-specific entry model when available, else the global one.

    For sectors that historically underperform with the global model (XLF/XLP/XLU),
    a sector-trained model captures the specific technical dynamics of that sector.
    Falls back to the global model when no sector-specific model exists.
    """
    sector_model = get_sector_entry_model(sector_etf)
    target_model = sector_model if sector_model is not None else get_entry_model()
    return predict_entry_prob(tech, vix, sector_etf, target_model)


def predict_live_prob(sig_dict: dict, model) -> float | None:
    """Return the signal-model win probability (0–1), or None on error/no model."""
    if model is None:
        return None
    try:
        import numpy as np
        import xgboost as xgb

        features = _extract_features(sig_dict)
        dm = xgb.DMatrix(np.array([features], dtype=float), feature_names=_FEATURE_NAMES)
        return float(model.predict(dm)[0])
    except Exception as e:
        log.debug(f"[signal_ml] predict_live_prob error: {e}")
        return None


def predict_entry_prob(
    tech: dict,
    vix: float | None,
    sector_etf: str | None,
    model,
) -> float | None:
    """Return the entry-model win probability (0–1), or None on error/no model."""
    if model is None:
        return None
    try:
        import numpy as np
        import xgboost as xgb
        from datetime import datetime

        now = datetime.now()
        features = _extract_entry_features(tech, vix, sector_etf, now.weekday(), now.month)
        dm = xgb.DMatrix(np.array([features], dtype=float), feature_names=_ENTRY_FEATURE_NAMES)
        return float(model.predict(dm)[0])
    except Exception as e:
        log.debug(f"[signal_ml] predict_entry_prob error: {e}")
        return None


def blend_confidence(
    base_conf: float,
    entry_prob: float | None,
    live_prob: float | None,
) -> float:
    """
    Blend entry and signal win-probs (50/50 when both available) and apply
    a single multiplicative ratio to base_conf.

    Falls back gracefully: uses whichever prob is available; returns base_conf
    unchanged when both are None.
    """
    if entry_prob is None and live_prob is None:
        return base_conf

    if entry_prob is not None and live_prob is not None:
        combined: float = 0.5 * entry_prob + 0.5 * live_prob
    else:
        combined = float(entry_prob if entry_prob is not None else live_prob)  # type: ignore[arg-type]

    base_win_prob = base_conf / 100.0 * 0.85
    ratio = combined / max(base_win_prob, 0.01)
    ratio = max(0.75, min(1.25, ratio))
    return round(min(_MAX_CONFIDENCE, base_conf * ratio), 1)
