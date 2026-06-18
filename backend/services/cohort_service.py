"""
services/cohort_service.py

QENG-6b: Shadow-control cohort framework.
QENG-6c: Policy versioning in every signal.

Deterministically routes active signals into experimental cohorts using MD5 hashes
and attaches policy versions to signal audit records.
"""

import hashlib
import logging
from datetime import datetime

from config import get_settings

log = logging.getLogger("signal.trade.cohort")

# Active policy versions (QENG-6c)
SCORING_POLICY_VERSION = "v10.3"
GATES_POLICY_VERSION = "v8.0"
ML_MODEL_ID = "xgb_classifier_v3.2"


def allocate_signal_cohort(
    ticker: str,
    ts: datetime,
    shadow_pct: int | None = None,
    withheld_pct: int | None = None,
) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - (100 - shadow - withheld)% Delivered (live/paper execution)
      - shadow% Shadow (silent logging only)
      - withheld% Withheld (control group)
    Percentages default to Settings. Set both to 0 to deliver every signal.
    """
    if shadow_pct is None or withheld_pct is None:
        settings = get_settings()
        shadow_pct = shadow_pct if shadow_pct is not None else settings.signal_cohort_shadow_pct
        withheld_pct = withheld_pct if withheld_pct is not None else settings.signal_cohort_withheld_pct

    # Clamp to valid ranges defensively.
    shadow_pct = max(0, min(100, shadow_pct))
    withheld_pct = max(0, min(100, withheld_pct))
    total = min(100, shadow_pct + withheld_pct)
    delivered_pct = 100 - total

    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode()
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)

    # Bucket [0..99]
    bucket = hash_val % 100

    if bucket < delivered_pct:
        return "delivered"
    elif bucket < delivered_pct + shadow_pct:
        return "shadow"
    else:
        return "withheld"


def build_policy_version_meta(ticker: str, ts: datetime, meta_prob: float = None) -> dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)

    return {
        "cohort": cohort,
        "policy_versions": {"scoring": SCORING_POLICY_VERSION, "gates": GATES_POLICY_VERSION, "ml_model": ML_MODEL_ID},
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat(),
    }
