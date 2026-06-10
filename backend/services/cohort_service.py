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

log = logging.getLogger("signal.trade.cohort")

# Active policy versions (QENG-6c)
SCORING_POLICY_VERSION = "v10.3"
GATES_POLICY_VERSION = "v8.0"
ML_MODEL_ID = "xgb_classifier_v3.2"


def allocate_signal_cohort(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode()
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)

    # Bucket [0..99]
    bucket = hash_val % 100

    if bucket < 70:
        return "delivered"
    elif bucket < 90:
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
