"""Cross-sectional alpha model — LIVE SHADOW scorer.

Loads the persisted cross-sectional models (h=21: data/cross_sectional_model.json;
h=63 quarterly variant: data/cross_sectional_model_h63.json, both trained by
`scripts/cross_sectional_alpha_model.py --save-model [--horizon 63]`) and scores
the current scan batch: the same price features the models train on, z-scored
ACROSS the batch (same recipe as cross_sectional_zscore), then model.predict →
percentile rank within the batch. The two horizons run in PARALLEL so their
forward series can arbitrate which ranking transfers to the live ~10d book.

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
# Parallel h=63 shadow (quarterly-rebalance variant validated 2026-06-11 via
# --nested-horizon: net 0.616, CI [+0.29,+0.94], selection haircut 0.000, cost-
# robust to 40bps, borrow breakeven ~700bps/yr). Scored alongside h=21 so the
# two forward series can arbitrate which horizon's ranking transfers to the
# live ~10d book. The §92 promotion criteria below apply to the h=21 field ONLY.
_MODEL_FILE_H63 = os.path.join(_DATA, "cross_sectional_model_h63.json")
_FEAT_FILE_H63 = os.path.join(_DATA, "cross_sectional_features_h63.json")

_MIN_NAMES = 10  # don't rank a thin cross-section (matches the backtest's MIN_NAMES_PER_DAY intent)
_Z_CLIP = 3.0

# §92: Pre-specified promotion criteria — locked BEFORE peeking at live shadow data.
# These criteria must be met before the bottom-decile sizing haircut is activated.
# Changing these criteria after viewing live data invalidates the forward test.
SHADOW_PROMOTION_CRITERIA = {
    "min_resolved_signals": 150,  # signals carrying crossSectionalShadowPct that have resolved
    "bottom_decile_wr_delta_pp": 3.0,  # bottom-decile live WR ≥3pp WORSE than rest
    "monotonic_direction": "top_gt_bottom",  # top decile WR ≥ bottom decile WR (directional)
    "sizing_haircut": 0.75,  # bottom-decile positionSizeScale multiplier when activated
    "decile_threshold": 10.0,  # percentile ≤ this qualifies as bottom decile
}

# Master switch — NEVER flip to True until check_promotion_criteria() returns True.
_SHADOW_SIZING_ACTIVE: bool = False

_cache: dict = {"model": None, "feature_cols": None, "loaded": False, "ok": False}
_cache_h63: dict = {"model": None, "feature_cols": None, "loaded": False, "ok": False}


def _load_into(cache: dict, model_file: str, feat_file: str, label: str) -> bool:
    """Lazy-load a persisted model + feature spec once. Returns False if absent."""
    if cache["loaded"]:
        return cache["ok"]
    cache["loaded"] = True
    try:
        if not (os.path.exists(model_file) and os.path.exists(feat_file)):
            return False
        import xgboost as xgb

        with open(feat_file) as f:
            meta = json.load(f)
        model = xgb.XGBRegressor()
        model.load_model(model_file)
        cache["model"] = model
        cache["feature_cols"] = list(meta["feature_cols"])
        cache["horizon"] = int(meta.get("horizon", 21))
        cache["ok"] = True
        log.info(
            "[cross_sectional_shadow] loaded %s model (%d features, horizon=%dd)",
            label,
            len(cache["feature_cols"]),
            cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] %s model unavailable (%s) — shadow scoring disabled", label, exc)
        return False


def _load() -> bool:
    """Lazy-load the persisted h=21 model + feature spec once."""
    return _load_into(_cache, _MODEL_FILE, _FEAT_FILE, "h=21")


def _load_h63() -> bool:
    """Lazy-load the persisted h=63 model + feature spec once."""
    return _load_into(_cache_h63, _MODEL_FILE_H63, _FEAT_FILE_H63, "h=63")


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


def _score_with(model, feature_cols: list[str], histories: dict[str, pd.DataFrame], label: str) -> dict[str, float]:
    """Shared scoring core: features → batch z-score → predict → percentile rank."""
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
        preds = model.predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] %s predict failed (%s)", label, exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def score_batch(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: h=21 cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    return _score_with(_cache["model"], _cache["feature_cols"], histories, "h=21")


def score_batch_h63(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: h=63 cross-sectional percentile 0-100} for the scan batch.

    Same contract as score_batch() but uses the quarterly-rebalance model
    (nested-horizon validated 2026-06-11). SHADOW ONLY — forward data collection
    in parallel with h=21; never feeds §92 promotion or sizing.
    """
    if not _load_h63():
        return {}
    return _score_with(_cache_h63["model"], _cache_h63["feature_cols"], histories, "h=63")


def check_promotion_criteria(
    resolved_shadow_signals: list[dict],
) -> tuple[bool, dict]:
    """
    Evaluate whether the pre-specified §92 promotion criteria are met.

    Args:
        resolved_shadow_signals: list of dicts with keys:
            - crossSectionalShadowPct (float)
            - outcome_14d (float | None): net return %, or None if unresolved

    Returns:
        (activated: bool, diagnostics: dict)
    """
    crit = SHADOW_PROMOTION_CRITERIA
    diag: dict = {
        "n_total": len(resolved_shadow_signals),
        "n_resolved": 0,
        "bottom_wr": None,
        "rest_wr": None,
        "top_wr": None,
        "monotonic": False,
        "activated": False,
    }

    resolved = [s for s in resolved_shadow_signals if s.get("outcome_14d") is not None]
    diag["n_resolved"] = len(resolved)
    if len(resolved) < crit["min_resolved_signals"]:
        return False, diag

    bottom = [s for s in resolved if s.get("crossSectionalShadowPct", 50) <= crit["decile_threshold"]]
    rest = [s for s in resolved if s.get("crossSectionalShadowPct", 50) > crit["decile_threshold"]]
    top = [s for s in resolved if s.get("crossSectionalShadowPct", 50) >= (100 - crit["decile_threshold"])]

    def _wr(signals: list[dict]) -> float | None:
        if not signals:
            return None
        wins = sum(1 for s in signals if s["outcome_14d"] > 0)
        return wins / len(signals) * 100.0

    diag["bottom_wr"] = _wr(bottom)
    diag["rest_wr"] = _wr(rest)
    diag["top_wr"] = _wr(top)

    if diag["bottom_wr"] is None or diag["rest_wr"] is None:
        return False, diag

    # Criterion 1: bottom-decile WR ≥3pp worse than the rest
    c1 = (diag["rest_wr"] - diag["bottom_wr"]) >= crit["bottom_decile_wr_delta_pp"]
    # Criterion 2: top-vs-bottom monotonic in at least direction
    c2 = (diag["top_wr"] or 0.0) >= diag["bottom_wr"]
    diag["monotonic"] = c2

    activated = c1 and c2
    diag["activated"] = activated
    return activated, diag


def apply_shadow_sizing(signals: list[dict]) -> None:
    """
    Apply the §92 bottom-decile sizing haircut when _SHADOW_SIZING_ACTIVE is True.
    Mutates signals in-place (modifies positionSizeScale on bottom-decile names).
    """
    if not _SHADOW_SIZING_ACTIVE:
        return
    crit = SHADOW_PROMOTION_CRITERIA
    for sig in signals:
        pct = sig.get("crossSectionalShadowPct")
        if pct is not None and pct <= crit["decile_threshold"]:
            sig["positionSizeScale"] = round(sig.get("positionSizeScale", 1.0) * crit["sizing_haircut"], 2)
            sig["rationale"] = list(sig.get("rationale", [])) + [
                {
                    "src": "Cross-Sectional Alpha (shadow)",
                    "head": "XS shadow: bottom-decile sizing haircut (§92)",
                    "body": (
                        f"Cross-sectional model places this name in the bottom {crit['decile_threshold']:.0f}% "
                        f"of predicted relative returns. Applying a {crit['sizing_haircut']:.0%} sizing "
                        "haircut per the pre-specified §92 promotion criteria."
                    ),
                    "sentiment": "neg",
                    "meta": f"xs_shadow_sizing=1 haircut={crit['sizing_haircut']}",
                }
            ]
