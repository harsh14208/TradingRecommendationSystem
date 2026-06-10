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

import numpy as np

log = logging.getLogger("signal.ml")

_DATA_DIR = Path(__file__).parent.parent / "data"
_MODEL_FILE = _DATA_DIR / "signal_ml_model.json"
_FEATURE_FILE = _DATA_DIR / "signal_ml_features.json"
_ENTRY_MODEL_FILE = _DATA_DIR / "backtest_ml_model.json"
_ENTRY_FEATURE_FILE = _DATA_DIR / "backtest_ml_features.json"
# A17 challenger: same 23 live features + raw_score as feature 24.
# Tests whether the heuristic point accumulator adds discriminating power
# beyond the structural features already in the signal model.
_CHALLENGER_MODEL_FILE = _DATA_DIR / "signal_ml_challenger_model.json"
_CHALLENGER_FEATURE_FILE = _DATA_DIR / "signal_ml_challenger_features.json"
# Meta-label model: predicts P(primary model is correct | context).
# Features include entry_prob as the key input — teaches the model WHEN
# the primary signal is reliable, not just which direction to trade.
_META_MODEL_FILE = _DATA_DIR / "meta_label_model.json"
_META_FEATURE_FILE = _DATA_DIR / "meta_label_features.json"

# Minimum CV-AUC for meta-model to be used live. Below this threshold the model
# adds noise rather than signal (QUANT_ENGINE_REVIEW §1.3).
_MIN_META_AUC = 0.52

_MAX_CONFIDENCE = 72.0

# Minimum resolved signals before we attempt training
_MIN_SAMPLES = 50
# Temporal train/test split — same philosophy as factor_miner.py
_TRAIN_SPLIT = 0.70
# Minimum live signals before deploying the live model.
# At N=300, Hanley-McNeil 95% CI on AUC spans ±0.055 (with balanced classes),
# making a 6pp improvement reliably detectable over the champion.
# Below N=300, a 4pp AUC gain has a ~40% chance of being sampling noise,
# making champion/challenger comparison statistically meaningless.
_MIN_LIVE_N_FOR_DEPLOYMENT = 300
# Minimum AUC improvement over champion to deploy challenger.
# Prevents noise-driven churn: at N=529, SE(AUC)≈0.022, so 0.005 ≈ 0.2 SE —
# a meaningful directional filter without requiring full statistical significance.
_MIN_AUC_DELTA_TO_DEPLOY = 0.005

# ── Module-level model caches ─────────────────────────────────────────────────
_model = None  # signal model (live DB)
_model_mtime: float = 0.0
_entry_model = None  # entry model (backtest)
_entry_model_mtime: float = 0.0
_meta_model = None  # meta-label model (triple-barrier relabeled backtest)
_meta_model_mtime: float = 0.0


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


def _check_feature_drift(features: list[float], label: str = "live") -> None:
    """Log warning if any feature drifts outside training P1/P99 bounds."""
    try:
        if not _FEATURE_FILE.exists():
            return
        meta = json.loads(_FEATURE_FILE.read_text())
        stats = meta.get("feature_stats", {})
        if not stats:
            # Only log once per process so we don't spam on every prediction
            if not getattr(_check_feature_drift, "_warned_missing_stats", False):
                log.info(
                    "[signal_ml] feature_stats absent in model metadata — drift monitor inactive until next retrain"
                )
                _check_feature_drift._warned_missing_stats = True
            return
        for i, name in enumerate(_FEATURE_NAMES):
            s = stats.get(name)
            if s is None:
                continue
            v = features[i]
            if math.isnan(v):
                continue
            lo, hi = s.get("p01"), s.get("p99")
            if lo is not None and v < lo:
                log.warning(
                    f"[signal_ml] {label} feature '{name}' = {v:.4f} below training P1 ({lo:.4f}) — distribution drift"
                )
            elif hi is not None and v > hi:
                log.warning(
                    f"[signal_ml] {label} feature '{name}' = {v:.4f} above training P99 ({hi:.4f}) — distribution drift"
                )
    except Exception:
        pass


# ── Feature extraction ─────────────────────────────────────────────────────────


def _extract_features(sig: dict) -> list[float]:
    """
    Extract the 23-feature structural vector from a signal dict.
    All values are available at generation time — no look-ahead.
    Intentionally excluded (circular dependency):
      - `confidence` / `sentiment`: Platt-scaled outputs of the heuristic scoring
        function; feeding them back as features creates a tautological loop where
        the ML model learns "high confidence → high win rate" rather than genuine
        new predictive content.
      - `raw_score`: the pre-scaling precursor to `confidence`. Although
        technically distinct, it captures the same alpha quality information as
        `confidence` (same inputs, same function body, only scaling differs).
        Including it would let the model circumvent the exclusion above by
        learning from the equivalent quantity one step earlier in the pipeline.
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
    # raw_score intentionally EXCLUDED — see docstring for circular dependency reasoning.

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
    ]


def _extract_challenger_features(sig: dict) -> list[float]:
    """
    A17 challenger feature vector: 23 structural features + raw_score (feature 24).

    raw_score is the heuristic point accumulator from generate_signal() before
    Platt calibration.  Including it here deliberately — the challenger model
    trains on [structural + heuristic] vs the signal model on [structural only].
    If challenger OOS AUC exceeds signal model by > _MIN_AUC_DELTA_TO_DEPLOY, the
    heuristic layer adds measurable discriminating power.  If not, the heuristic
    score is redundant given the structural features.
    """
    base = _extract_features(sig)
    raw = sig.get("raw_score")
    return base + [float(raw) if raw is not None else float("nan")]


# 23 features — raw_score removed (circular dependency with confidence, see _extract_features docstring)
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
    # "raw_score" intentionally removed — circular dependency with confidence
]

# A17 challenger: 23 structural features + raw_score as feature 24.
_CHALLENGER_FEATURE_NAMES = _FEATURE_NAMES + ["raw_score"]


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


# ── AUC confidence interval ───────────────────────────────────────────────────


def auc_ci_95(auc: float, n_pos: int, n_neg: int) -> tuple[float, float]:
    """Hanley-McNeil (1982) 95% CI for an AUC estimate.

    SE(AUC) = sqrt((AUC*(1-AUC) + (n_pos-1)*(Q1-AUC^2) + (n_neg-1)*(Q2-AUC^2))
                   / (n_pos * n_neg))
    where Q1 = AUC/(2-AUC)  and  Q2 = 2*AUC^2/(1+AUC).

    Returns (lo_95, hi_95) clamped to [0.0, 1.0].
    Requires n_pos >= 1 and n_neg >= 1; returns (0.0, 1.0) when data is absent.
    """
    if n_pos < 1 or n_neg < 1:
        return (0.0, 1.0)
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc**2 / (1.0 + auc)
    variance = (auc * (1.0 - auc) + (n_pos - 1) * (q1 - auc**2) + (n_neg - 1) * (q2 - auc**2)) / (n_pos * n_neg)
    se = math.sqrt(max(variance, 0.0))
    return (max(0.0, auc - 1.96 * se), min(1.0, auc + 1.96 * se))


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

    if len(rows) < _MIN_LIVE_N_FOR_DEPLOYMENT:
        log.warning(
            f"[signal_ml] N={len(rows)} < _MIN_LIVE_N_FOR_DEPLOYMENT={_MIN_LIVE_N_FOR_DEPLOYMENT}. "
            "Training for diagnostics only — model will NOT be deployed. "
            "At this sample size, the Hanley-McNeil 95% CI on AUC spans ±0.07+, "
            "making champion/challenger comparison unreliable."
        )
        _training_only = True
    else:
        _training_only = False

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

    # NaN-rate guard: if any feature is >20% missing, the model is training on
    # a degraded distribution.  Log loudly so telemetry catches it.
    _X_arr = np.array(X, dtype=float)
    _nan_rate = np.isnan(_X_arr).mean(axis=0)
    for _i, _rate in enumerate(_nan_rate):
        if _rate > 0.20:
            log.critical(
                f"[signal_ml] Feature '{_FEATURE_NAMES[_i]}' is {_rate:.1%} NaN — "
                "model training on degraded distribution. Check data pipeline."
            )

    # ── Temporal train/test split ──────────────────────────────────────────────
    split = max(int(len(X) * _TRAIN_SPLIT), _MIN_SAMPLES)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Require ≥15 OOS samples before the AUC estimate is trustworthy enough for
    # champion/challenger comparison. At N=5, the 95% CI on AUC spans ±0.22,
    # making any comparison statistically meaningless. At N=15 it narrows to ±0.13.
    if len(X_test) < 15:
        log.info(
            f"[signal_ml] OOS test set too small ({len(X_test)} < 15 samples) — "
            "AUC would be unreliable. Skipping to protect champion model."
        )
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
            # Hanley-McNeil 95% CI — essential context for champion/challenger comparison.
            _n_pos = int(sum(y_test))
            _n_neg = n_test - _n_pos
            _auc_lo, _auc_hi = auc_ci_95(oos_auc, _n_pos, _n_neg)
            log.info(
                f"[signal_ml] OOS — accuracy={oos_acc:.3f}  precision={oos_prec:.3f}  "
                f"recall={oos_rec:.3f}  AUC={oos_auc}  AUC_95CI=[{_auc_lo:.4f},{_auc_hi:.4f}]"
            )
        else:
            oos_auc = None
            _auc_lo = _auc_hi = None
            log.info(
                f"[signal_ml] OOS — accuracy={oos_acc:.3f}  precision={oos_prec:.3f}  recall={oos_rec:.3f}  AUC=None (single class)"
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
    # Only deploy the new model if it beats the current champion on the SAME
    # test set.  Previously the comparison was across different windows
    # (challenger's newest 30% vs champion's older stored window), which at
    # N_test≈170 has SE≈0.04 — 8× the 0.005 threshold.  Now both models are
    # scored on the identical held-out fold.
    _deployed = False
    _champion_auc_stored: Optional[float] = None
    _champion_auc_same_window: Optional[float] = None
    try:
        if _FEATURE_FILE.exists():
            _champ_meta = json.loads(_FEATURE_FILE.read_text())
            _champion_auc_stored = _champ_meta.get("oos_auc")
    except Exception:
        pass

    # Score champion on the SAME test fold so the comparison is fair.
    if _MODEL_FILE.exists() and len(set(y_test)) > 1:
        try:
            _champ_booster = xgb.Booster()
            _champ_booster.load_model(str(_MODEL_FILE))
            _champ_dm = xgb.DMatrix(
                np.array(X_test, dtype=float),
                feature_names=_FEATURE_NAMES,
            )
            _champ_prob = _champ_booster.predict(_champ_dm)
            _champion_auc_same_window = round(float(roc_auc_score(y_test, _champ_prob)), 4)
            log.info(
                f"[signal_ml] Champion re-scored on current test fold: "
                f"AUC={_champion_auc_same_window:.4f} (stored={_champion_auc_stored})"
            )
        except (xgb.core.XGBoostError, OSError, Exception) as _ce:
            log.warning(f"[signal_ml] Could not re-score champion on current fold: {_ce}")
            _champion_auc_same_window = None

    # Use the same-window AUC when available; fall back to stored AUC only
    # when the champion file is missing (first-run scenario).
    _champion_auc = _champion_auc_same_window if _champion_auc_same_window is not None else _champion_auc_stored

    # Deploy only when the OOS AUC is computable, beats the champion by at least
    # _MIN_AUC_DELTA_TO_DEPLOY, and N_live >= _MIN_LIVE_N_FOR_DEPLOYMENT.
    #
    # Gate layers:
    #   1. _training_only — N < _MIN_LIVE_N_FOR_DEPLOYMENT: skip deployment entirely.
    #   2. oos_auc is None — single-class test set: do NOT deploy (degenerate sample).
    #   3. _champion_auc is None — no existing champion: deploy on first run only.
    #   4. oos_auc > _champion_auc + _MIN_AUC_DELTA — challenger must exceed champion
    #      by the minimum meaningful delta on the SAME test window.
    _should_deploy = (
        not _training_only  # N gate: enough live data for reliable AUC estimate
        and (
            _champion_auc is None  # first run — no champion to protect
            or (
                oos_auc is not None  # valid AUC (≥2 classes in test set)
                and oos_auc > _champion_auc + _MIN_AUC_DELTA_TO_DEPLOY  # meaningful improvement
            )
        )
    )

    if _should_deploy:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            model.get_booster().save_model(str(_MODEL_FILE))
            _deployed = True
            if _champion_auc is None or oos_auc is None:
                log.info(f"[signal_ml] First model deployed — OOS AUC={oos_auc}")
            else:
                _delta = oos_auc - _champion_auc
                _window_note = "same-window" if _champion_auc_same_window is not None else "stored-window"
                log.info(
                    f"[signal_ml] Challenger deployed — OOS AUC {oos_auc:.4f} > "
                    f"champion {_champion_auc:.4f} ({_window_note}) (Δ+{_delta:.4f} > min {_MIN_AUC_DELTA_TO_DEPLOY})"
                )
        except Exception as e:
            log.error(f"[signal_ml] WRITE FAILED — {_MODEL_FILE}: {e}")
    elif _training_only:
        log.warning(
            f"[signal_ml] Training-only run (N={len(rows)} < {_MIN_LIVE_N_FOR_DEPLOYMENT}) — "
            "model not deployed. Increase resolved signal count before champion/challenger comparison."
        )
    elif oos_auc is not None and _champion_auc is not None:
        _delta = oos_auc - _champion_auc
        _window_note = "same-window" if _champion_auc_same_window is not None else "stored-window"
        log.warning(
            f"[signal_ml] Challenger rejected — OOS AUC {oos_auc:.4f} vs champion "
            f"{_champion_auc:.4f} ({_window_note}) (Δ{_delta:+.4f}, min required +{_MIN_AUC_DELTA_TO_DEPLOY}). "
            "Keeping existing model."
        )
    else:
        log.warning(
            f"[signal_ml] Challenger rejected — oos_auc={oos_auc} (single-class or None). Keeping existing model."
        )

    # Store per-feature training bounds for drift monitoring
    _X_arr = np.array(X, dtype=float)
    feature_stats = {}
    for i, name in enumerate(_FEATURE_NAMES):
        col = _X_arr[:, i]
        col_valid = col[~np.isnan(col)]
        if len(col_valid) > 0:
            feature_stats[name] = {
                "p01": round(float(np.percentile(col_valid, 1)), 6),
                "p99": round(float(np.percentile(col_valid, 99)), 6),
                "median": round(float(np.median(col_valid)), 6),
                "mean": round(float(np.mean(col_valid)), 6),
                "std": round(float(np.std(col_valid)), 6),
            }

    # ── Persist feature importances + metadata ─────────────────────────────────
    from datetime import datetime as _dt

    _auc_lo_out = round(_auc_lo, 4) if _auc_lo is not None else None
    _auc_hi_out = round(_auc_hi, 4) if _auc_hi is not None else None
    metadata = {
        "trained_at": _dt.utcnow().isoformat(),
        "n_train": n_train,
        "n_test": n_test,
        "n_total": len(rows),
        "feature_stats": feature_stats,
        "oos_accuracy": oos_acc,
        "oos_auc": oos_auc,
        "oos_auc_ci_95": [_auc_lo_out, _auc_hi_out],
        "oos_precision": oos_prec,
        "oos_recall": oos_rec,
        "top_features": top_features,
        "feature_importances": fi,
        "deployed": _deployed,
        "training_only": _training_only,
        "champion_auc": _champion_auc,
        "min_live_n_for_deployment": _MIN_LIVE_N_FOR_DEPLOYMENT,
        "min_auc_delta_to_deploy": _MIN_AUC_DELTA_TO_DEPLOY,
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
        "oos_auc_ci_95": [_auc_lo_out, _auc_hi_out],
        "oos_precision": oos_prec,
        "oos_recall": oos_rec,
        "n_train": n_train,
        "n_test": n_test,
        "n_total": len(rows),
        "top_features": top_features,
        "deployed": _deployed,
        "training_only": _training_only,
        "champion_auc": _champion_auc,
    }


def train_challenger_model() -> Optional[dict]:
    """
    A17: Train the challenger model — 23 structural features + raw_score (feature 24).

    Tests whether the heuristic point accumulator (raw_score) adds discriminating
    power beyond what the structural features already encode.

    Deployment logic:
      - Loads the same resolved-signal DB rows as train_model()
      - Trains XGBoost on _CHALLENGER_FEATURE_NAMES (24 features)
      - Compares OOS AUC vs the current signal model's AUC (from _FEATURE_FILE)
      - Saves challenger to _CHALLENGER_MODEL_FILE only if delta > _MIN_AUC_DELTA_TO_DEPLOY
      - Returns interpretation: what the AUC delta means for the heuristic layer

    Requires _MIN_LIVE_N_FOR_DEPLOYMENT (300) resolved signals for deployment.
    """
    try:
        import xgboost as xgb
    except ImportError:
        log.warning("[signal_ml] xgboost not installed — skipping train_challenger_model()")
        return None

    try:
        from sklearn.metrics import roc_auc_score
    except ImportError:
        log.warning("[signal_ml] scikit-learn not installed — skipping train_challenger_model()")
        return None

    try:
        rows = _load_resolved_signals_sync()
    except Exception as e:
        log.warning(f"[signal_ml] A17 DB read failed: {e}")
        return None

    if len(rows) < _MIN_SAMPLES:
        log.info(f"[signal_ml] A17: only {len(rows)} resolved signals — need {_MIN_SAMPLES}. Skipping.")
        return None

    _training_only = len(rows) < _MIN_LIVE_N_FOR_DEPLOYMENT

    rows.sort(key=lambda r: r.get("created_at") or "")

    X, y = [], []
    for r in rows:
        action = (r.get("action") or "").upper()
        outcome_pct = r.get("outcome_pct")
        if action not in ("BUY", "SELL") or outcome_pct is None:
            continue
        label = 1 if (action == "BUY" and outcome_pct > 0) or (action == "SELL" and outcome_pct < 0) else 0
        X.append(_extract_challenger_features(r))
        y.append(label)

    if len(X) < _MIN_SAMPLES:
        return None

    split = max(int(len(X) * _TRAIN_SPLIT), _MIN_SAMPLES)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    if len(X_test) < 15:
        log.info(f"[signal_ml] A17: OOS set too small ({len(X_test)}) — skipping.")
        return None

    try:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.7,
            gamma=0.3,
            reg_alpha=0.1,
            reg_lambda=2.0,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(X_train, y_train, verbose=False)
    except Exception as e:
        log.warning(f"[signal_ml] A17 XGBoost training failed: {e}")
        return None

    try:
        y_prob = model.predict_proba(X_test)[:, 1]
        if len(set(y_test)) < 2:
            log.warning("[signal_ml] A17: single class in test set — cannot compute AUC.")
            return None
        challenger_auc = round(float(roc_auc_score(y_test, y_prob)), 4)
    except Exception as e:
        log.warning(f"[signal_ml] A17 evaluation failed: {e}")
        return None

    # Load current signal model AUC for comparison
    baseline_auc: Optional[float] = None
    try:
        if _FEATURE_FILE.exists():
            baseline_auc = json.loads(_FEATURE_FILE.read_text()).get("oos_auc")
    except Exception:
        pass

    delta = (challenger_auc - baseline_auc) if baseline_auc is not None else None

    # Interpretation: does the heuristic layer add value?
    if delta is None:
        interpretation = "No baseline signal model to compare against — cannot evaluate."
    elif delta > _MIN_AUC_DELTA_TO_DEPLOY:
        interpretation = (
            f"raw_score adds +{delta:.4f} AUC over structural features alone. "
            "The heuristic scoring layer has measurable discriminating power. Keep it."
        )
    else:
        interpretation = (
            f"raw_score adds only {delta:+.4f} AUC (threshold: +{_MIN_AUC_DELTA_TO_DEPLOY}). "
            "The heuristic scoring layer appears redundant at this sample size — "
            "structural features already encode the same information."
        )

    log.info(f"[signal_ml] A17 challenger AUC={challenger_auc:.4f} | baseline={baseline_auc} | {interpretation}")

    # Deploy challenger only if it clears the AUC delta bar and we have enough data
    _deployed = False
    _should_deploy = not _training_only and delta is not None and delta > _MIN_AUC_DELTA_TO_DEPLOY
    if _should_deploy:
        try:
            _DATA_DIR.mkdir(parents=True, exist_ok=True)
            model.get_booster().save_model(str(_CHALLENGER_MODEL_FILE))
            _deployed = True
            log.info(f"[signal_ml] A17 challenger deployed to {_CHALLENGER_MODEL_FILE}")
        except Exception as e:
            log.error(f"[signal_ml] A17 WRITE FAILED — {_CHALLENGER_MODEL_FILE}: {e}")
    elif not _should_deploy and _CHALLENGER_MODEL_FILE.exists():
        # Remove stale challenger if it no longer clears the bar on new data
        try:
            _CHALLENGER_MODEL_FILE.unlink()
            log.info("[signal_ml] A17: stale challenger removed (delta below threshold on retraining).")
        except Exception:
            pass

    # Feature importances
    try:
        importances = model.feature_importances_.tolist()
        fi = sorted(
            [{"feature": n, "importance": round(float(v), 5)} for n, v in zip(_CHALLENGER_FEATURE_NAMES, importances)],
            key=lambda x: -x["importance"],
        )
        raw_score_rank = next((i + 1 for i, f in enumerate(fi) if f["feature"] == "raw_score"), None)
    except Exception:
        fi = []
        raw_score_rank = None

    from datetime import datetime as _dt

    metadata = {
        "trained_at": _dt.utcnow().isoformat(),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_total": len(rows),
        "challenger_auc": challenger_auc,
        "baseline_auc": baseline_auc,
        "delta": round(delta, 4) if delta is not None else None,
        "deployed": _deployed,
        "training_only": _training_only,
        "raw_score_importance_rank": raw_score_rank,
        "feature_importances": fi,
        "interpretation": interpretation,
    }
    try:
        _CHALLENGER_FEATURE_FILE.write_text(json.dumps(metadata, indent=2))
    except Exception as e:
        log.error(f"[signal_ml] A17 metadata write failed: {e}")

    return metadata


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


# ── A17 Challenger model cache ────────────────────────────────────────────────
_challenger_model = None
_challenger_model_mtime: float = 0.0


def get_challenger_model():
    """Return the A17 challenger model (23 features + raw_score), or None if absent.

    The challenger file is only written by train_challenger_model() when the
    24-feature model improves OOS AUC by > _MIN_AUC_DELTA_TO_DEPLOY over the
    23-feature signal model.  If the file is absent the challenger hasn't
    cleared the deployment bar — blend_confidence falls back to 2-way blend.
    """
    global _challenger_model, _challenger_model_mtime

    if not _CHALLENGER_MODEL_FILE.exists():
        return None

    try:
        current_mtime = _CHALLENGER_MODEL_FILE.stat().st_mtime
    except OSError:
        return _challenger_model

    if _challenger_model is None or current_mtime != _challenger_model_mtime:
        try:
            import xgboost as xgb

            b = xgb.Booster()
            b.load_model(str(_CHALLENGER_MODEL_FILE))
            _challenger_model = b
            _challenger_model_mtime = current_mtime
            log.info("[signal_ml] A17 challenger model loaded/reloaded from disk")
        except Exception as e:
            log.warning(f"[signal_ml] Failed to load challenger model: {e}")
            _challenger_model = None

    return _challenger_model


def validate_feature_schema(features: list, expected_names: list) -> bool:
    """TSYS-7b: Validate feature vector shape and types before inference."""
    if len(features) != len(expected_names):
        log.error(f"[schema_val] Length mismatch: got {len(features)} features, expected {len(expected_names)}")
        return False
    for i, val in enumerate(features):
        if val is None:
            continue
        if not isinstance(val, (int, float)):
            log.error(
                f"[schema_val] Type shift detected for feature '{expected_names[i]}' at index {i}: value={val} type={type(val)}"
            )
            return False
    return True


def predict_challenger_prob(sig_dict: dict, model) -> "float | None":
    """Return the A17 challenger win probability (0–1), or None on error/no model.

    Uses the 24-feature vector (23 structural + raw_score) to test whether the
    heuristic point accumulator adds discriminating power at inference time.
    """
    if model is None:
        return None
    try:
        import numpy as np
        import xgboost as xgb

        features = _extract_challenger_features(sig_dict)
        if not validate_feature_schema(features, _CHALLENGER_FEATURE_NAMES):
            log.error("[signal_ml] Schema validation failed for predict_challenger_prob")
            return None
        dm = xgb.DMatrix(
            np.array([features], dtype=float),
            feature_names=_CHALLENGER_FEATURE_NAMES,
        )
        return float(model.predict(dm)[0])
    except Exception as e:
        log.debug(f"[signal_ml] predict_challenger_prob error: {e}")
        return None


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
        _check_feature_drift(features, label="live")
        if not validate_feature_schema(features, _FEATURE_NAMES):
            log.error("[signal_ml] Schema validation failed for predict_live_prob")
            return None
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
        _check_feature_drift(features, label="entry")
        if not validate_feature_schema(features, _ENTRY_FEATURE_NAMES):
            log.error("[signal_ml] Schema validation failed for predict_entry_prob")
            return None
        dm = xgb.DMatrix(np.array([features], dtype=float), feature_names=_ENTRY_FEATURE_NAMES)
        return float(model.predict(dm)[0])
    except Exception as e:
        log.debug(f"[signal_ml] predict_entry_prob error: {e}")
        return None


# ── Meta-label model ─────────────────────────────────────────────────────────
# 11-feature vector available at signal-generation time.
# Key insight: entry_prob is the primary model output — the meta-label model
# learns *when* the primary model is reliable, not just direction.
_META_FEATURE_NAMES = [
    "entry_prob",  # output of the entry XGBoost model (THE key feature)
    "ou_halflife",  # OU mean-reversion speed
    "hurst",  # Hurst exponent
    "vix",  # macro fear level
    "atr_pct",  # annualised volatility
    "rvol",  # relative volume vs 20d avg
    "hmm_bull_prob",  # HMM P(bull) — macro regime
    "hmm_trans_risk",  # HMM transition risk
    "dte_bucket",  # earnings proximity (0–3)
    "sector_ord",  # sector ETF ordinal
    "dow",  # day of week
    "vix_term_ratio",  # VIX / VIX3M ratio
    "sector_momentum",  # 5-day sector ETF return
    "vix_9d_ratio",  # VIX9D / VIX ratio
    "ff_str",  # Fama-French Short-Term Reversal factor
]


def _extract_meta_features(
    tech: dict,
    entry_prob: float | None,
    hmm_regime: dict | None,
    vix: float | None,
    sector_etf: str | None,
    dow: int | None,
    dte: int | None,
    vix_term_ratio: float | None = None,
    sector_momentum: float | None = None,
    vix_9d_ratio: float | None = None,
    ff_str: float | None = None,
) -> list[float]:
    """Build the 15-feature meta-label vector."""

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
    atr_val = tech.get("atr") or 0.0
    try:
        atr_pct = float(atr_val) / float(price) * 100.0 if float(price) > 0 else float("nan")
    except (TypeError, ValueError):
        atr_pct = float("nan")

    hmm = hmm_regime or {}

    vix_tr = vix_term_ratio if vix_term_ratio is not None else tech.get("vix_term_ratio")
    if vix_tr is None:
        vix_tr = float("nan")

    sec_mom = sector_momentum if sector_momentum is not None else tech.get("sector_momentum")
    if sec_mom is None:
        sec_mom = float("nan")

    vix_9d = vix_9d_ratio if vix_9d_ratio is not None else tech.get("vix_9d_ratio")
    if vix_9d is None:
        vix_9d = float("nan")

    _ff_str = ff_str if ff_str is not None else tech.get("ff_str")
    if _ff_str is None:
        _ff_str = float("nan")

    return [
        float(entry_prob) if entry_prob is not None else float("nan"),
        _f("ou_halflife"),
        _f("hurst"),
        float(vix) if vix is not None else float("nan"),
        atr_pct,
        _f("rvol"),
        float(hmm.get("bull_prob", 0.5)),
        float(hmm.get("transition_risk", 0.1)),
        _dte_bucket(dte),
        _sector_ord(sector_etf),
        float(dow) if dow is not None else float("nan"),
        float(vix_tr),
        float(sec_mom),
        float(vix_9d),
        float(_ff_str),
    ]


def get_meta_model():
    """Load meta-label XGBoost model from disk, caching by mtime.

    Returns None when the model file is missing OR when the stored CV-AUC is
    below _MIN_META_AUC (default 0.52).  This prevents a weak meta-model from
    degrading live confidence blends.
    """
    global _meta_model, _meta_model_mtime
    try:
        import xgboost as xgb

        if not _META_MODEL_FILE.exists():
            return None
        mtime = _META_MODEL_FILE.stat().st_mtime
        if _meta_model is not None and mtime == _meta_model_mtime:
            return _meta_model

        # Quality gate: check stored CV-AUC before loading into memory
        if _META_FEATURE_FILE.exists():
            _meta_meta = json.loads(_META_FEATURE_FILE.read_text())
            _cv_auc = float(_meta_meta.get("cv_auc_mean") or 0.0)
            if _cv_auc < _MIN_META_AUC:
                log.warning(
                    "[signal_ml] Meta-model CV-AUC %.3f < %.3f threshold — disabled until retrain improves it",
                    _cv_auc,
                    _MIN_META_AUC,
                )
                return None

        m = xgb.Booster()
        m.load_model(str(_META_MODEL_FILE))
        _meta_model = m
        _meta_model_mtime = mtime
        log.info("[signal_ml] Meta-label model loaded from %s", _META_MODEL_FILE.name)
        return m
    except Exception as e:
        log.debug("[signal_ml] Meta model load: %s", e)
        return None


def predict_meta_prob(
    tech: dict,
    entry_prob: float | None,
    hmm_regime: dict | None,
    vix: float | None,
    sector_etf: str | None,
    dte: int | None,
    vix_term_ratio: float | None = None,
    sector_momentum: float | None = None,
    vix_9d_ratio: float | None = None,
    ff_str: float | None = None,
) -> float | None:
    """
    Predict P(primary model is correct | context) using the meta-label model.

    Returns None when the model is absent or inputs are invalid.
    Used to scale the final blend_confidence ratio: high meta_prob amplifies,
    low meta_prob dampens.
    """
    model = get_meta_model()
    if model is None:
        return None
    try:
        import numpy as np
        import xgboost as xgb
        from datetime import datetime

        now = datetime.now()
        feats = _extract_meta_features(
            tech,
            entry_prob,
            hmm_regime,
            vix,
            sector_etf,
            now.weekday(),
            dte,
            vix_term_ratio=vix_term_ratio,
            sector_momentum=sector_momentum,
            vix_9d_ratio=vix_9d_ratio,
            ff_str=ff_str,
        )
        _check_feature_drift(feats, label="meta")
        dm = xgb.DMatrix(np.array([feats], dtype=float), feature_names=_META_FEATURE_NAMES)
        return float(model.predict(dm)[0])
    except Exception as e:
        log.debug("[signal_ml] predict_meta_prob error: %s", e)
        return None


def blend_confidence(
    base_conf: float,
    entry_prob: float | None,
    live_prob: float | None,
    challenger_prob: float | None = None,
    meta_prob: float | None = None,
) -> float:
    """
    Blend entry, signal, and (optionally) A17 challenger win-probs and apply
    a single multiplicative ratio to base_conf.

    Available probs are averaged with equal weight.  Falls back gracefully:
    returns base_conf unchanged when all three are None.

    challenger_prob is only non-None when the A17 challenger model has cleared
    the deployment bar (AUC delta > _MIN_AUC_DELTA_TO_DEPLOY).

    meta_prob, when provided, further scales the blended ratio:
        meta_scale = 0.60 + 0.80 × meta_prob  →  [0.60, 1.40]
    This lets the meta-label model amplify high-conviction signals and
    dampen signals where context is hostile to the primary prediction.
    """
    probs = [p for p in (entry_prob, live_prob, challenger_prob) if p is not None]
    if not probs:
        return base_conf

    combined: float = sum(probs) / len(probs)
    base_win_prob = base_conf / 100.0 * 0.85
    ratio = combined / max(base_win_prob, 0.01)
    ratio = max(0.75, min(1.25, ratio))

    # Meta-label scaling: meta_prob=0.5 → no change; 0.9 → amplify; 0.2 → dampen
    if meta_prob is not None:
        meta_scale = 0.60 + 0.80 * float(meta_prob)
        meta_scale = max(0.60, min(1.40, meta_scale))
        ratio = max(0.75, min(1.25, ratio * meta_scale))

    return round(min(_MAX_CONFIDENCE, base_conf * ratio), 1)


# ── ML-4: Rolling AUC drift monitor ──────────────────────────────────────────


def compute_rolling_auc(window_days: int = 90) -> dict:
    """
    ML-4: Compute champion model AUC on a rolling window of live resolved signals.

    Uses confidence as the model score and outcome_pct>0 as the positive label.
    Runs synchronously so it can be called from scripts or health-check endpoints.

    Returns dict: {auc, n, window_days, status} where status ∈ {ok, warn, degrade, insufficient_n, no_db}.
    Logs a WARNING when AUC dips below the warn threshold.
    """
    import os
    import sqlite3
    from datetime import datetime, timedelta

    AUC_WARN = 0.58
    AUC_DEGRADE = 0.55

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trading.db")
    if not os.path.exists(db_path):
        return {"auc": None, "n": 0, "window_days": window_days, "status": "no_db"}

    cutoff = (datetime.now() - timedelta(days=window_days)).isoformat()
    try:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT confidence, outcome_pct FROM signals "
            "WHERE outcome_pct IS NOT NULL AND confidence IS NOT NULL "
            "AND created_at >= ? ORDER BY created_at DESC",
            (cutoff,),
        ).fetchall()
        conn.close()
    except Exception as exc:
        return {"auc": None, "n": 0, "window_days": window_days, "status": f"db_error: {exc}"}

    if len(rows) < 20:
        return {"auc": None, "n": len(rows), "window_days": window_days, "status": "insufficient_n"}

    # ROC-AUC via trapezoidal rule (Mann-Whitney U form)
    scores = [(float(r[0]) / 100.0, 1 if float(r[1]) > 0 else 0) for r in rows]
    scores.sort(key=lambda x: -x[0])
    pos = sum(y for _, y in scores)
    neg = len(scores) - pos
    if pos == 0 or neg == 0:
        return {"auc": None, "n": len(scores), "window_days": window_days, "status": "no_variance"}

    tp, fp, auc_val, prev_fp = 0, 0, 0.0, 0
    for _, y in scores:
        if y == 1:
            tp += 1
        else:
            fp += 1
            auc_val += tp * (fp - prev_fp)
            prev_fp = fp
    auc_val /= pos * neg

    status = "ok" if auc_val >= AUC_WARN else ("warn" if auc_val >= AUC_DEGRADE else "degrade")
    if status in ("warn", "degrade"):
        import logging

        logging.getLogger("signal_ml").warning(
            "ML-4 AUC drift: rolling %dd AUC=%.4f [%s] (warn<%.2f, degrade<%.2f)",
            window_days,
            auc_val,
            status,
            AUC_WARN,
            AUC_DEGRADE,
        )
    return {"auc": round(auc_val, 4), "n": len(scores), "window_days": window_days, "status": status}
