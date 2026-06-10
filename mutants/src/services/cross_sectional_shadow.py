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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x__load__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__load__mutmut)
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


def x__load__mutmut_orig() -> bool:
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


def x__load__mutmut_1() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["XXloadedXX"]:
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


def x__load__mutmut_2() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["LOADED"]:
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


def x__load__mutmut_3() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["XXokXX"]
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


def x__load__mutmut_4() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["OK"]
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


def x__load__mutmut_5() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = None
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


def x__load__mutmut_6() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["XXloadedXX"] = True
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


def x__load__mutmut_7() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["LOADED"] = True
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


def x__load__mutmut_8() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = False
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


def x__load__mutmut_9() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
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


def x__load__mutmut_10() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) or os.path.exists(_FEAT_FILE)):
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


def x__load__mutmut_11() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(None) and os.path.exists(_FEAT_FILE)):
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


def x__load__mutmut_12() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(None)):
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


def x__load__mutmut_13() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
            return True
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


def x__load__mutmut_14() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
            return False
        import xgboost as xgb

        with open(None) as f:
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


def x__load__mutmut_15() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
            return False
        import xgboost as xgb

        with open(_FEAT_FILE) as f:
            meta = None
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


def x__load__mutmut_16() -> bool:
    """Lazy-load the persisted model + feature spec once. Returns False if absent."""
    if _cache["loaded"]:
        return _cache["ok"]
    _cache["loaded"] = True
    try:
        if not (os.path.exists(_MODEL_FILE) and os.path.exists(_FEAT_FILE)):
            return False
        import xgboost as xgb

        with open(_FEAT_FILE) as f:
            meta = json.load(None)
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


def x__load__mutmut_17() -> bool:
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
        model = None
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


def x__load__mutmut_18() -> bool:
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
        model.load_model(None)
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


def x__load__mutmut_19() -> bool:
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
        _cache["model"] = None
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


def x__load__mutmut_20() -> bool:
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
        _cache["XXmodelXX"] = model
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


def x__load__mutmut_21() -> bool:
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
        _cache["MODEL"] = model
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


def x__load__mutmut_22() -> bool:
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
        _cache["feature_cols"] = None
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


def x__load__mutmut_23() -> bool:
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
        _cache["XXfeature_colsXX"] = list(meta["feature_cols"])
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


def x__load__mutmut_24() -> bool:
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
        _cache["FEATURE_COLS"] = list(meta["feature_cols"])
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


def x__load__mutmut_25() -> bool:
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
        _cache["feature_cols"] = list(None)
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


def x__load__mutmut_26() -> bool:
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
        _cache["feature_cols"] = list(meta["XXfeature_colsXX"])
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


def x__load__mutmut_27() -> bool:
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
        _cache["feature_cols"] = list(meta["FEATURE_COLS"])
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


def x__load__mutmut_28() -> bool:
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
        _cache["horizon"] = None
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


def x__load__mutmut_29() -> bool:
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
        _cache["XXhorizonXX"] = int(meta.get("horizon", 21))
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


def x__load__mutmut_30() -> bool:
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
        _cache["HORIZON"] = int(meta.get("horizon", 21))
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


def x__load__mutmut_31() -> bool:
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
        _cache["horizon"] = int(None)
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


def x__load__mutmut_32() -> bool:
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
        _cache["horizon"] = int(meta.get(None, 21))
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


def x__load__mutmut_33() -> bool:
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
        _cache["horizon"] = int(meta.get("horizon", None))
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


def x__load__mutmut_34() -> bool:
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
        _cache["horizon"] = int(meta.get(21))
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


def x__load__mutmut_35() -> bool:
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
        _cache["horizon"] = int(meta.get("horizon", ))
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


def x__load__mutmut_36() -> bool:
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
        _cache["horizon"] = int(meta.get("XXhorizonXX", 21))
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


def x__load__mutmut_37() -> bool:
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
        _cache["horizon"] = int(meta.get("HORIZON", 21))
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


def x__load__mutmut_38() -> bool:
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
        _cache["horizon"] = int(meta.get("horizon", 22))
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


def x__load__mutmut_39() -> bool:
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
        _cache["ok"] = None
        log.info(
            "[cross_sectional_shadow] loaded model (%d features, horizon=%dd)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_40() -> bool:
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
        _cache["XXokXX"] = True
        log.info(
            "[cross_sectional_shadow] loaded model (%d features, horizon=%dd)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_41() -> bool:
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
        _cache["OK"] = True
        log.info(
            "[cross_sectional_shadow] loaded model (%d features, horizon=%dd)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_42() -> bool:
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
        _cache["ok"] = False
        log.info(
            "[cross_sectional_shadow] loaded model (%d features, horizon=%dd)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_43() -> bool:
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
            None,
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_44() -> bool:
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
            None,
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_45() -> bool:
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
            None,
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_46() -> bool:
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
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_47() -> bool:
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
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_48() -> bool:
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
            )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_49() -> bool:
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
            "XX[cross_sectional_shadow] loaded model (%d features, horizon=%dd)XX",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_50() -> bool:
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
            "[CROSS_SECTIONAL_SHADOW] LOADED MODEL (%D FEATURES, HORIZON=%DD)",
            len(_cache["feature_cols"]),
            _cache["horizon"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_51() -> bool:
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
            _cache["XXhorizonXX"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_52() -> bool:
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
            _cache["HORIZON"],
        )
        return True
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_53() -> bool:
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
        return False
    except Exception as exc:  # missing xgboost, corrupt artifact, etc.
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", exc)
        return False


def x__load__mutmut_54() -> bool:
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
        log.warning(None, exc)
        return False


def x__load__mutmut_55() -> bool:
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
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", None)
        return False


def x__load__mutmut_56() -> bool:
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
        log.warning(exc)
        return False


def x__load__mutmut_57() -> bool:
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
        log.warning("[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabled", )
        return False


def x__load__mutmut_58() -> bool:
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
        log.warning("XX[cross_sectional_shadow] model unavailable (%s) — shadow scoring disabledXX", exc)
        return False


def x__load__mutmut_59() -> bool:
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
        log.warning("[CROSS_SECTIONAL_SHADOW] MODEL UNAVAILABLE (%S) — SHADOW SCORING DISABLED", exc)
        return False


def x__load__mutmut_60() -> bool:
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
        return True

mutants_x__load__mutmut['_mutmut_orig'] = x__load__mutmut_orig # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_1'] = x__load__mutmut_1 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_2'] = x__load__mutmut_2 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_3'] = x__load__mutmut_3 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_4'] = x__load__mutmut_4 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_5'] = x__load__mutmut_5 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_6'] = x__load__mutmut_6 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_7'] = x__load__mutmut_7 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_8'] = x__load__mutmut_8 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_9'] = x__load__mutmut_9 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_10'] = x__load__mutmut_10 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_11'] = x__load__mutmut_11 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_12'] = x__load__mutmut_12 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_13'] = x__load__mutmut_13 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_14'] = x__load__mutmut_14 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_15'] = x__load__mutmut_15 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_16'] = x__load__mutmut_16 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_17'] = x__load__mutmut_17 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_18'] = x__load__mutmut_18 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_19'] = x__load__mutmut_19 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_20'] = x__load__mutmut_20 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_21'] = x__load__mutmut_21 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_22'] = x__load__mutmut_22 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_23'] = x__load__mutmut_23 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_24'] = x__load__mutmut_24 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_25'] = x__load__mutmut_25 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_26'] = x__load__mutmut_26 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_27'] = x__load__mutmut_27 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_28'] = x__load__mutmut_28 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_29'] = x__load__mutmut_29 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_30'] = x__load__mutmut_30 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_31'] = x__load__mutmut_31 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_32'] = x__load__mutmut_32 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_33'] = x__load__mutmut_33 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_34'] = x__load__mutmut_34 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_35'] = x__load__mutmut_35 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_36'] = x__load__mutmut_36 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_37'] = x__load__mutmut_37 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_38'] = x__load__mutmut_38 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_39'] = x__load__mutmut_39 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_40'] = x__load__mutmut_40 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_41'] = x__load__mutmut_41 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_42'] = x__load__mutmut_42 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_43'] = x__load__mutmut_43 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_44'] = x__load__mutmut_44 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_45'] = x__load__mutmut_45 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_46'] = x__load__mutmut_46 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_47'] = x__load__mutmut_47 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_48'] = x__load__mutmut_48 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_49'] = x__load__mutmut_49 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_50'] = x__load__mutmut_50 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_51'] = x__load__mutmut_51 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_52'] = x__load__mutmut_52 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_53'] = x__load__mutmut_53 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_54'] = x__load__mutmut_54 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_55'] = x__load__mutmut_55 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_56'] = x__load__mutmut_56 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_57'] = x__load__mutmut_57 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_58'] = x__load__mutmut_58 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_59'] = x__load__mutmut_59 # type: ignore # mutmut generated
mutants_x__load__mutmut['x__load__mutmut_60'] = x__load__mutmut_60 # type: ignore # mutmut generated
mutants_x__price_features__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__price_features__mutmut)
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


def x__price_features__mutmut_orig(df: pd.DataFrame) -> dict[str, float] | None:
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


def x__price_features__mutmut_1(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = None
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


def x__price_features__mutmut_2(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "XXCloseXX" if "Close" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_3(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_4(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "CLOSE" if "Close" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_5(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "XXCloseXX" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_6(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "close" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_7(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "CLOSE" in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_8(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" not in df.columns else ("close" if "close" in df.columns else None)
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


def x__price_features__mutmut_9(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("XXcloseXX" if "close" in df.columns else None)
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


def x__price_features__mutmut_10(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("CLOSE" if "close" in df.columns else None)
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


def x__price_features__mutmut_11(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "XXcloseXX" in df.columns else None)
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


def x__price_features__mutmut_12(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "CLOSE" in df.columns else None)
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


def x__price_features__mutmut_13(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" not in df.columns else None)
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


def x__price_features__mutmut_14(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = None
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


def x__price_features__mutmut_15(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "XXVolumeXX" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_16(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_17(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "VOLUME" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_18(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "XXVolumeXX" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_19(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "volume" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_20(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "VOLUME" in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_21(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" not in df.columns else ("volume" if "volume" in df.columns else None)
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


def x__price_features__mutmut_22(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("XXvolumeXX" if "volume" in df.columns else None)
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


def x__price_features__mutmut_23(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("VOLUME" if "volume" in df.columns else None)
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


def x__price_features__mutmut_24(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "XXvolumeXX" in df.columns else None)
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


def x__price_features__mutmut_25(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "VOLUME" in df.columns else None)
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


def x__price_features__mutmut_26(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" not in df.columns else None)
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


def x__price_features__mutmut_27(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None and len(df) < 253:
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


def x__price_features__mutmut_28(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None and vol_col is None or len(df) < 253:
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


def x__price_features__mutmut_29(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is not None or vol_col is None or len(df) < 253:
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


def x__price_features__mutmut_30(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is not None or len(df) < 253:
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


def x__price_features__mutmut_31(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) <= 253:
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


def x__price_features__mutmut_32(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 254:
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


def x__price_features__mutmut_33(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = None
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


def x__price_features__mutmut_34(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(None, errors="coerce")
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


def x__price_features__mutmut_35(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors=None)
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


def x__price_features__mutmut_36(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(errors="coerce")
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


def x__price_features__mutmut_37(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], )
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


def x__price_features__mutmut_38(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="XXcoerceXX")
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


def x__price_features__mutmut_39(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="COERCE")
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


def x__price_features__mutmut_40(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = None
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


def x__price_features__mutmut_41(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(None, errors="coerce")
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


def x__price_features__mutmut_42(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors=None)
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


def x__price_features__mutmut_43(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(errors="coerce")
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


def x__price_features__mutmut_44(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], )
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


def x__price_features__mutmut_45(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="XXcoerceXX")
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


def x__price_features__mutmut_46(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="COERCE")
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


def x__price_features__mutmut_47(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = None
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


def x__price_features__mutmut_48(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = None
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


def x__price_features__mutmut_49(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=None, adjust=False).mean()
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


def x__price_features__mutmut_50(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=None).mean()
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


def x__price_features__mutmut_51(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(adjust=False).mean()
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


def x__price_features__mutmut_52(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, ).mean()
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


def x__price_features__mutmut_53(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=None).ewm(alpha=1 / 14, adjust=False).mean()
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


def x__price_features__mutmut_54(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=1.0).ewm(alpha=1 / 14, adjust=False).mean()
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


def x__price_features__mutmut_55(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 * 14, adjust=False).mean()
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


def x__price_features__mutmut_56(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=2 / 14, adjust=False).mean()
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


def x__price_features__mutmut_57(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 15, adjust=False).mean()
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


def x__price_features__mutmut_58(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=True).mean()
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


def x__price_features__mutmut_59(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = None
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


def x__price_features__mutmut_60(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=None, adjust=False).mean()
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


def x__price_features__mutmut_61(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 / 14, adjust=None).mean()
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


def x__price_features__mutmut_62(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(adjust=False).mean()
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


def x__price_features__mutmut_63(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 / 14, ).mean()
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


def x__price_features__mutmut_64(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (+close.diff().clip(upper=0.0)).ewm(alpha=1 / 14, adjust=False).mean()
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


def x__price_features__mutmut_65(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=None)).ewm(alpha=1 / 14, adjust=False).mean()
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


def x__price_features__mutmut_66(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=1.0)).ewm(alpha=1 / 14, adjust=False).mean()
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


def x__price_features__mutmut_67(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 * 14, adjust=False).mean()
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


def x__price_features__mutmut_68(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=2 / 14, adjust=False).mean()
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


def x__price_features__mutmut_69(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 / 15, adjust=False).mean()
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


def x__price_features__mutmut_70(df: pd.DataFrame) -> dict[str, float] | None:
    """Latest-row price features, matching cross_sectional_alpha_model.add_price_features."""
    close_col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
    vol_col = "Volume" if "Volume" in df.columns else ("volume" if "volume" in df.columns else None)
    if close_col is None or vol_col is None or len(df) < 253:
        return None
    close = pd.to_numeric(df[close_col], errors="coerce")
    volume = pd.to_numeric(df[vol_col], errors="coerce")
    ret1 = close.pct_change()
    gain = close.diff().clip(lower=0.0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-close.diff().clip(upper=0.0)).ewm(alpha=1 / 14, adjust=True).mean()
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


def x__price_features__mutmut_71(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = None
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


def x__price_features__mutmut_72(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain * loss.replace(0.0, np.nan)
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


def x__price_features__mutmut_73(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain / loss.replace(None, np.nan)
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


def x__price_features__mutmut_74(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain / loss.replace(0.0, None)
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


def x__price_features__mutmut_75(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain / loss.replace(np.nan)
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


def x__price_features__mutmut_76(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain / loss.replace(0.0, )
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


def x__price_features__mutmut_77(df: pd.DataFrame) -> dict[str, float] | None:
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
    rs = gain / loss.replace(1.0, np.nan)
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


def x__price_features__mutmut_78(df: pd.DataFrame) -> dict[str, float] | None:
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
    feats = None
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_79(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXmom_12_1XX": close.shift(21).iloc[-1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_80(df: pd.DataFrame) -> dict[str, float] | None:
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
        "MOM_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_81(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[-1] + 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_82(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] * close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_83(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(None).iloc[-1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_84(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(22).iloc[-1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_85(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[+1] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_86(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-2] / close.shift(252).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_87(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(None).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_88(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(253).iloc[-1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_89(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[+1] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_90(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[-2] - 1.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_91(df: pd.DataFrame) -> dict[str, float] | None:
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
        "mom_12_1": close.shift(21).iloc[-1] / close.shift(252).iloc[-1] - 2.0,
        "rev_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_92(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXrev_5XX": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_93(df: pd.DataFrame) -> dict[str, float] | None:
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
        "REV_5": close.iloc[-1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_94(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-1] / close.iloc[-6] + 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_95(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-1] * close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_96(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[+1] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_97(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-2] / close.iloc[-6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_98(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-1] / close.iloc[+6] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_99(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-1] / close.iloc[-7] - 1.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_100(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_5": close.iloc[-1] / close.iloc[-6] - 2.0,
        "rev_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_101(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXrev_21XX": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_102(df: pd.DataFrame) -> dict[str, float] | None:
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
        "REV_21": close.iloc[-1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_103(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-1] / close.iloc[-22] + 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_104(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-1] * close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_105(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[+1] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_106(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-2] / close.iloc[-22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_107(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-1] / close.iloc[+22] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_108(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-1] / close.iloc[-23] - 1.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_109(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rev_21": close.iloc[-1] / close.iloc[-22] - 2.0,
        "vol_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_110(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXvol_21XX": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_111(df: pd.DataFrame) -> dict[str, float] | None:
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
        "VOL_21": ret1.rolling(21).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_112(df: pd.DataFrame) -> dict[str, float] | None:
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
        "vol_21": ret1.rolling(None).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_113(df: pd.DataFrame) -> dict[str, float] | None:
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
        "vol_21": ret1.rolling(22).std().iloc[-1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_114(df: pd.DataFrame) -> dict[str, float] | None:
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
        "vol_21": ret1.rolling(21).std().iloc[+1],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_115(df: pd.DataFrame) -> dict[str, float] | None:
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
        "vol_21": ret1.rolling(21).std().iloc[-2],
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_116(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXdollar_vol_21XX": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_117(df: pd.DataFrame) -> dict[str, float] | None:
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
        "DOLLAR_VOL_21": (close * volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_118(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dollar_vol_21": (close * volume).rolling(None).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_119(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dollar_vol_21": (close / volume).rolling(21).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_120(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dollar_vol_21": (close * volume).rolling(22).mean().iloc[-1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_121(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[+1],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_122(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dollar_vol_21": (close * volume).rolling(21).mean().iloc[-2],
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_123(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXdist_ma50XX": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_124(df: pd.DataFrame) -> dict[str, float] | None:
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
        "DIST_MA50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_125(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] + 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_126(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] * close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_127(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[+1] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_128(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-2] / close.rolling(50).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_129(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(None).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_130(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(51).mean().iloc[-1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_131(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[+1] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_132(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-2] - 1.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_133(df: pd.DataFrame) -> dict[str, float] | None:
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
        "dist_ma50": close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 2.0,
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_134(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXrsi_14XX": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_135(df: pd.DataFrame) -> dict[str, float] | None:
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
        "RSI_14": (100 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_136(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 + 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_137(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (101 - 100 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_138(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 100 * (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_139(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 101 / (1 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_140(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 100 / (1 - rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_141(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 100 / (2 + rs)).iloc[-1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_142(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 100 / (1 + rs)).iloc[+1],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_143(df: pd.DataFrame) -> dict[str, float] | None:
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
        "rsi_14": (100 - 100 / (1 + rs)).iloc[-2],
        "days_since_earn": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_144(df: pd.DataFrame) -> dict[str, float] | None:
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
        "XXdays_since_earnXX": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_145(df: pd.DataFrame) -> dict[str, float] | None:
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
        "DAYS_SINCE_EARN": np.nan,  # not available in the live scan context → neutralized to 0 in z-score
    }
    return {k: (float(v) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_146(df: pd.DataFrame) -> dict[str, float] | None:
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
    return {k: (float(None) if pd.notna(v) else np.nan) for k, v in feats.items()}


def x__price_features__mutmut_147(df: pd.DataFrame) -> dict[str, float] | None:
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
    return {k: (float(v) if pd.notna(None) else np.nan) for k, v in feats.items()}

mutants_x__price_features__mutmut['_mutmut_orig'] = x__price_features__mutmut_orig # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_1'] = x__price_features__mutmut_1 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_2'] = x__price_features__mutmut_2 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_3'] = x__price_features__mutmut_3 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_4'] = x__price_features__mutmut_4 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_5'] = x__price_features__mutmut_5 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_6'] = x__price_features__mutmut_6 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_7'] = x__price_features__mutmut_7 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_8'] = x__price_features__mutmut_8 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_9'] = x__price_features__mutmut_9 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_10'] = x__price_features__mutmut_10 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_11'] = x__price_features__mutmut_11 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_12'] = x__price_features__mutmut_12 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_13'] = x__price_features__mutmut_13 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_14'] = x__price_features__mutmut_14 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_15'] = x__price_features__mutmut_15 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_16'] = x__price_features__mutmut_16 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_17'] = x__price_features__mutmut_17 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_18'] = x__price_features__mutmut_18 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_19'] = x__price_features__mutmut_19 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_20'] = x__price_features__mutmut_20 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_21'] = x__price_features__mutmut_21 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_22'] = x__price_features__mutmut_22 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_23'] = x__price_features__mutmut_23 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_24'] = x__price_features__mutmut_24 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_25'] = x__price_features__mutmut_25 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_26'] = x__price_features__mutmut_26 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_27'] = x__price_features__mutmut_27 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_28'] = x__price_features__mutmut_28 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_29'] = x__price_features__mutmut_29 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_30'] = x__price_features__mutmut_30 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_31'] = x__price_features__mutmut_31 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_32'] = x__price_features__mutmut_32 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_33'] = x__price_features__mutmut_33 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_34'] = x__price_features__mutmut_34 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_35'] = x__price_features__mutmut_35 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_36'] = x__price_features__mutmut_36 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_37'] = x__price_features__mutmut_37 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_38'] = x__price_features__mutmut_38 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_39'] = x__price_features__mutmut_39 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_40'] = x__price_features__mutmut_40 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_41'] = x__price_features__mutmut_41 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_42'] = x__price_features__mutmut_42 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_43'] = x__price_features__mutmut_43 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_44'] = x__price_features__mutmut_44 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_45'] = x__price_features__mutmut_45 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_46'] = x__price_features__mutmut_46 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_47'] = x__price_features__mutmut_47 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_48'] = x__price_features__mutmut_48 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_49'] = x__price_features__mutmut_49 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_50'] = x__price_features__mutmut_50 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_51'] = x__price_features__mutmut_51 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_52'] = x__price_features__mutmut_52 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_53'] = x__price_features__mutmut_53 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_54'] = x__price_features__mutmut_54 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_55'] = x__price_features__mutmut_55 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_56'] = x__price_features__mutmut_56 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_57'] = x__price_features__mutmut_57 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_58'] = x__price_features__mutmut_58 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_59'] = x__price_features__mutmut_59 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_60'] = x__price_features__mutmut_60 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_61'] = x__price_features__mutmut_61 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_62'] = x__price_features__mutmut_62 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_63'] = x__price_features__mutmut_63 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_64'] = x__price_features__mutmut_64 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_65'] = x__price_features__mutmut_65 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_66'] = x__price_features__mutmut_66 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_67'] = x__price_features__mutmut_67 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_68'] = x__price_features__mutmut_68 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_69'] = x__price_features__mutmut_69 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_70'] = x__price_features__mutmut_70 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_71'] = x__price_features__mutmut_71 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_72'] = x__price_features__mutmut_72 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_73'] = x__price_features__mutmut_73 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_74'] = x__price_features__mutmut_74 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_75'] = x__price_features__mutmut_75 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_76'] = x__price_features__mutmut_76 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_77'] = x__price_features__mutmut_77 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_78'] = x__price_features__mutmut_78 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_79'] = x__price_features__mutmut_79 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_80'] = x__price_features__mutmut_80 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_81'] = x__price_features__mutmut_81 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_82'] = x__price_features__mutmut_82 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_83'] = x__price_features__mutmut_83 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_84'] = x__price_features__mutmut_84 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_85'] = x__price_features__mutmut_85 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_86'] = x__price_features__mutmut_86 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_87'] = x__price_features__mutmut_87 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_88'] = x__price_features__mutmut_88 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_89'] = x__price_features__mutmut_89 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_90'] = x__price_features__mutmut_90 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_91'] = x__price_features__mutmut_91 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_92'] = x__price_features__mutmut_92 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_93'] = x__price_features__mutmut_93 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_94'] = x__price_features__mutmut_94 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_95'] = x__price_features__mutmut_95 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_96'] = x__price_features__mutmut_96 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_97'] = x__price_features__mutmut_97 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_98'] = x__price_features__mutmut_98 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_99'] = x__price_features__mutmut_99 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_100'] = x__price_features__mutmut_100 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_101'] = x__price_features__mutmut_101 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_102'] = x__price_features__mutmut_102 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_103'] = x__price_features__mutmut_103 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_104'] = x__price_features__mutmut_104 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_105'] = x__price_features__mutmut_105 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_106'] = x__price_features__mutmut_106 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_107'] = x__price_features__mutmut_107 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_108'] = x__price_features__mutmut_108 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_109'] = x__price_features__mutmut_109 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_110'] = x__price_features__mutmut_110 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_111'] = x__price_features__mutmut_111 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_112'] = x__price_features__mutmut_112 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_113'] = x__price_features__mutmut_113 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_114'] = x__price_features__mutmut_114 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_115'] = x__price_features__mutmut_115 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_116'] = x__price_features__mutmut_116 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_117'] = x__price_features__mutmut_117 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_118'] = x__price_features__mutmut_118 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_119'] = x__price_features__mutmut_119 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_120'] = x__price_features__mutmut_120 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_121'] = x__price_features__mutmut_121 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_122'] = x__price_features__mutmut_122 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_123'] = x__price_features__mutmut_123 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_124'] = x__price_features__mutmut_124 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_125'] = x__price_features__mutmut_125 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_126'] = x__price_features__mutmut_126 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_127'] = x__price_features__mutmut_127 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_128'] = x__price_features__mutmut_128 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_129'] = x__price_features__mutmut_129 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_130'] = x__price_features__mutmut_130 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_131'] = x__price_features__mutmut_131 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_132'] = x__price_features__mutmut_132 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_133'] = x__price_features__mutmut_133 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_134'] = x__price_features__mutmut_134 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_135'] = x__price_features__mutmut_135 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_136'] = x__price_features__mutmut_136 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_137'] = x__price_features__mutmut_137 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_138'] = x__price_features__mutmut_138 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_139'] = x__price_features__mutmut_139 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_140'] = x__price_features__mutmut_140 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_141'] = x__price_features__mutmut_141 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_142'] = x__price_features__mutmut_142 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_143'] = x__price_features__mutmut_143 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_144'] = x__price_features__mutmut_144 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_145'] = x__price_features__mutmut_145 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_146'] = x__price_features__mutmut_146 # type: ignore # mutmut generated
mutants_x__price_features__mutmut['x__price_features__mutmut_147'] = x__price_features__mutmut_147 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_score_batch__mutmut)
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


def x_score_batch__mutmut_orig(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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


def x_score_batch__mutmut_1(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if _load():
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


def x_score_batch__mutmut_2(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    feature_cols = None
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


def x_score_batch__mutmut_3(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    feature_cols = _cache["XXfeature_colsXX"]
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


def x_score_batch__mutmut_4(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    feature_cols = _cache["FEATURE_COLS"]
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


def x_score_batch__mutmut_5(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Return {ticker: cross-sectional percentile 0-100} for the scan batch.

    Percentile is the model's predicted relative-return rank WITHIN this batch
    (100 = strongest predicted relative performer, 0 = weakest). {} if the model
    is unavailable or the batch is too thin to rank.
    """
    if not _load():
        return {}
    feature_cols = _cache["feature_cols"]
    rows: dict[str, dict[str, float]] = None
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


def x_score_batch__mutmut_6(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None and getattr(df, "empty", True):
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


def x_score_batch__mutmut_7(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is not None or getattr(df, "empty", True):
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


def x_score_batch__mutmut_8(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(None, "empty", True):
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


def x_score_batch__mutmut_9(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, None, True):
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


def x_score_batch__mutmut_10(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, "empty", None):
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


def x_score_batch__mutmut_11(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr("empty", True):
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


def x_score_batch__mutmut_12(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, True):
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


def x_score_batch__mutmut_13(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, "empty", ):
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


def x_score_batch__mutmut_14(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, "XXemptyXX", True):
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


def x_score_batch__mutmut_15(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, "EMPTY", True):
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


def x_score_batch__mutmut_16(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if df is None or getattr(df, "empty", False):
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


def x_score_batch__mutmut_17(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
            break
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


def x_score_batch__mutmut_18(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        f = None
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


def x_score_batch__mutmut_19(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        f = _price_features(None)
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


def x_score_batch__mutmut_20(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        if f is None:
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


def x_score_batch__mutmut_21(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
            rows[ticker] = None
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


def x_score_batch__mutmut_22(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    if len(rows) <= _MIN_NAMES:
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


def x_score_batch__mutmut_23(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = None
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


def x_score_batch__mutmut_24(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(None, orient="index")[feature_cols]
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


def x_score_batch__mutmut_25(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(rows, orient=None)[feature_cols]
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


def x_score_batch__mutmut_26(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(orient="index")[feature_cols]
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


def x_score_batch__mutmut_27(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(rows, )[feature_cols]
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


def x_score_batch__mutmut_28(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(rows, orient="XXindexXX")[feature_cols]
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


def x_score_batch__mutmut_29(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    fm = pd.DataFrame.from_dict(rows, orient="INDEX")[feature_cols]
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


def x_score_batch__mutmut_30(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = None
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_31(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(None, axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_32(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=None)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_33(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_34(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), )
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_35(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(None, axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_36(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=None).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_37(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_38(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), ).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_39(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=None), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_40(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=1), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_41(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=2).div(fm.std(axis=0).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_42(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(None, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_43(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, None), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_44(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_45(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, ), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_46(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=None).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_47(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=1).replace(0.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_48(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(1.0, np.nan), axis=1)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_49(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = fm.sub(fm.mean(axis=0), axis=1).div(fm.std(axis=0).replace(0.0, np.nan), axis=2)
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_50(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = None

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_51(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(None)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_52(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(None, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_53(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(-_Z_CLIP, None).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_54(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(_Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_55(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(-_Z_CLIP, ).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_56(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(+_Z_CLIP, _Z_CLIP).fillna(0.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_57(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    z = z.clip(-_Z_CLIP, _Z_CLIP).fillna(1.0)

    try:
        preds = _cache["model"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_58(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        preds = None
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_59(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        preds = _cache["model"].predict(None)
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_60(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        preds = _cache["XXmodelXX"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_61(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        preds = _cache["MODEL"].predict(z.values.astype(float))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_62(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        preds = _cache["model"].predict(z.values.astype(None))
    except Exception as exc:
        log.warning("[cross_sectional_shadow] predict failed (%s)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_63(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning(None, exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_64(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning("[cross_sectional_shadow] predict failed (%s)", None)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_65(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning(exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_66(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning("[cross_sectional_shadow] predict failed (%s)", )
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_67(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning("XX[cross_sectional_shadow] predict failed (%s)XX", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_68(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
        log.warning("[CROSS_SECTIONAL_SHADOW] PREDICT FAILED (%S)", exc)
        return {}

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_69(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = None
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_70(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, index=z.index).rank(pct=True) / 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_71(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, index=z.index).rank(pct=None) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_72(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(None, index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_73(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, index=None).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_74(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(index=z.index).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_75(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, ).rank(pct=True) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_76(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, index=z.index).rank(pct=False) * 100.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_77(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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

    pct = pd.Series(preds, index=z.index).rank(pct=True) * 101.0
    return {t: round(float(p), 1) for t, p in pct.items()}


def x_score_batch__mutmut_78(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(None, 1) for t, p in pct.items()}


def x_score_batch__mutmut_79(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(float(p), None) for t, p in pct.items()}


def x_score_batch__mutmut_80(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(1) for t, p in pct.items()}


def x_score_batch__mutmut_81(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(float(p), ) for t, p in pct.items()}


def x_score_batch__mutmut_82(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(float(None), 1) for t, p in pct.items()}


def x_score_batch__mutmut_83(histories: dict[str, pd.DataFrame]) -> dict[str, float]:
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
    return {t: round(float(p), 2) for t, p in pct.items()}

mutants_x_score_batch__mutmut['_mutmut_orig'] = x_score_batch__mutmut_orig # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_1'] = x_score_batch__mutmut_1 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_2'] = x_score_batch__mutmut_2 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_3'] = x_score_batch__mutmut_3 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_4'] = x_score_batch__mutmut_4 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_5'] = x_score_batch__mutmut_5 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_6'] = x_score_batch__mutmut_6 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_7'] = x_score_batch__mutmut_7 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_8'] = x_score_batch__mutmut_8 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_9'] = x_score_batch__mutmut_9 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_10'] = x_score_batch__mutmut_10 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_11'] = x_score_batch__mutmut_11 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_12'] = x_score_batch__mutmut_12 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_13'] = x_score_batch__mutmut_13 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_14'] = x_score_batch__mutmut_14 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_15'] = x_score_batch__mutmut_15 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_16'] = x_score_batch__mutmut_16 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_17'] = x_score_batch__mutmut_17 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_18'] = x_score_batch__mutmut_18 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_19'] = x_score_batch__mutmut_19 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_20'] = x_score_batch__mutmut_20 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_21'] = x_score_batch__mutmut_21 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_22'] = x_score_batch__mutmut_22 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_23'] = x_score_batch__mutmut_23 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_24'] = x_score_batch__mutmut_24 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_25'] = x_score_batch__mutmut_25 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_26'] = x_score_batch__mutmut_26 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_27'] = x_score_batch__mutmut_27 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_28'] = x_score_batch__mutmut_28 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_29'] = x_score_batch__mutmut_29 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_30'] = x_score_batch__mutmut_30 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_31'] = x_score_batch__mutmut_31 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_32'] = x_score_batch__mutmut_32 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_33'] = x_score_batch__mutmut_33 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_34'] = x_score_batch__mutmut_34 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_35'] = x_score_batch__mutmut_35 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_36'] = x_score_batch__mutmut_36 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_37'] = x_score_batch__mutmut_37 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_38'] = x_score_batch__mutmut_38 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_39'] = x_score_batch__mutmut_39 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_40'] = x_score_batch__mutmut_40 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_41'] = x_score_batch__mutmut_41 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_42'] = x_score_batch__mutmut_42 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_43'] = x_score_batch__mutmut_43 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_44'] = x_score_batch__mutmut_44 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_45'] = x_score_batch__mutmut_45 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_46'] = x_score_batch__mutmut_46 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_47'] = x_score_batch__mutmut_47 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_48'] = x_score_batch__mutmut_48 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_49'] = x_score_batch__mutmut_49 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_50'] = x_score_batch__mutmut_50 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_51'] = x_score_batch__mutmut_51 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_52'] = x_score_batch__mutmut_52 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_53'] = x_score_batch__mutmut_53 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_54'] = x_score_batch__mutmut_54 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_55'] = x_score_batch__mutmut_55 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_56'] = x_score_batch__mutmut_56 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_57'] = x_score_batch__mutmut_57 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_58'] = x_score_batch__mutmut_58 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_59'] = x_score_batch__mutmut_59 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_60'] = x_score_batch__mutmut_60 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_61'] = x_score_batch__mutmut_61 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_62'] = x_score_batch__mutmut_62 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_63'] = x_score_batch__mutmut_63 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_64'] = x_score_batch__mutmut_64 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_65'] = x_score_batch__mutmut_65 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_66'] = x_score_batch__mutmut_66 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_67'] = x_score_batch__mutmut_67 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_68'] = x_score_batch__mutmut_68 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_69'] = x_score_batch__mutmut_69 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_70'] = x_score_batch__mutmut_70 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_71'] = x_score_batch__mutmut_71 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_72'] = x_score_batch__mutmut_72 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_73'] = x_score_batch__mutmut_73 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_74'] = x_score_batch__mutmut_74 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_75'] = x_score_batch__mutmut_75 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_76'] = x_score_batch__mutmut_76 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_77'] = x_score_batch__mutmut_77 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_78'] = x_score_batch__mutmut_78 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_79'] = x_score_batch__mutmut_79 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_80'] = x_score_batch__mutmut_80 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_81'] = x_score_batch__mutmut_81 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_82'] = x_score_batch__mutmut_82 # type: ignore # mutmut generated
mutants_x_score_batch__mutmut['x_score_batch__mutmut_83'] = x_score_batch__mutmut_83 # type: ignore # mutmut generated
