"""Cross-sectional alpha model — LIVE SHADOW scorer.

Loads the persisted h=21 cross-sectional model (data/cross_sectional_model.json,
trained by `scripts/cross_sectional_alpha_model.py --save-model`) and scores the
current scan batch: the same price features the model trains on, z-scored ACROSS
the batch (same recipe as cross_sectional_zscore), then model.predict → percentile
rank within the batch.

SHADOW ONLY. The caller attaches the percentile to signals for observability and
logging; it MUST NOT change action / confidence / positionSizeScale until the thin
h=21 edge is forward-validated (90% CI grazes 0; IC ~0.002; the live ~10-day-hold
watchlist context also differs from the validated 21-day full-S&P setup). Returns
{} on any failure (missing model, xgboost unavailable, thin batch) so the live
engine degrades gracefully.
"""

from __future__ import annotations

import json
import logging
import os

import numpy as np
import pandas as pd

log = logging.getLogger("signal.trade.cross_sectional_shadow")

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_MODEL_FILE = os.path.join(_DATA, "cross_sectional_model.json")
_FEAT_FILE = os.path.join(_DATA, "cross_sectional_features.json")

_MIN_NAMES = 10  # don't rank a thin cross-section (matches the backtest's MIN_NAMES_PER_DAY intent)
_Z_CLIP = 3.0

_cache: dict = {"model": None, "feature_cols": None, "loaded": False, "ok": False}


def _load() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
            return False
        import xgboost as xgb

        with open(_FEAT_FILE) as f:
            meta = json.load(f)
        model = xgb.XGBRegressor()
        model.load_model(_MODEL_FILE)
        _cache["model"] = model
        _cache["feature_cols"] = list(meta["feature_cols"])
        _cache["horizon"] = int(meta.get("horizon", 21))
        _cache["ok"] = True
        log.info(
            "[cross_sectional_shadow] loaded model (%d features, horizon=%dd)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def _price_features(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0.0, np.nan)
    feats = {
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def score_batch(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    feature_cols = _cache["feature_cols"]
    rows: dict[str, dict[str, float]] = {}
    for ticker, df in histories.items():
        if df is None or getattr(df, "empty", True):
            continue
        f = _price_features(df)
        if f is not None:
            rows[ticker] = f
    if len(rows) < _MIN_NAMES:
        return {}

    fm = pd.DataFrame.from_dict(rows, orient="index")[feature_cols]
    # Cross-sectional z-score across the batch, clip ±3, neutralize NaN → 0
    # (same normalization as cross_sectional_zscore in the backtest).
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}
