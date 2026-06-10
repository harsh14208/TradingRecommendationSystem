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
from typing import Dict, Tuple

log = logging.getLogger("signal.trade.cohort")

# Active policy versions (QENG-6c)
SCORING_POLICY_VERSION = "v10.3"
GATES_POLICY_VERSION = "v8.0"
ML_MODEL_ID = "xgb_classifier_v3.2"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_allocate_signal_cohort__mutmut: MutantDict = {}  # type: ignore

@_mutmut_mutated(mutants_x_allocate_signal_cohort__mutmut)
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
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_orig(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_1(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = None
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_2(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime(None)
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_3(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("XX%Y-%m-%d %H:%M:%SXX")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_4(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%y-%m-%d %h:%m:%s")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_5(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%M-%D %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_6(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = None
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_7(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode(None)
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_8(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("XXutf-8XX")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_9(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("UTF-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_10(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = None
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_11(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(None, 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_12(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), None)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_13(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_14(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), )
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_15(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(None).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_16(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 17)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_17(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = None
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_18(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val / 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_19(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 101
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_20(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket <= 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_21(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 71:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_22(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "XXdeliveredXX"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_23(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "DELIVERED"
    elif bucket < 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_24(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket <= 90:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_25(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 91:
        return "shadow"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_26(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "XXshadowXX"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_27(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "SHADOW"
    else:
        return "withheld"

def x_allocate_signal_cohort__mutmut_28(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "XXwithheldXX"

def x_allocate_signal_cohort__mutmut_29(ticker: str, ts: datetime) -> str:
    """
    QENG-6b: Deterministic hash-based cohort routing.
    Splits signals into experimental groups:
      - 70% Delivered (live/paper execution)
      - 20% Shadow (silent logging only)
      - 10% Withheld (withheld control group to measure adverse selection)
    """
    # Deterministic hash of ticker + timestamp string
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    seed = f"{ticker}:{ts_str}".encode("utf-8")
    hash_val = int(hashlib.md5(seed).hexdigest(), 16)
    
    # Bucket [0..99]
    bucket = hash_val % 100
    
    if bucket < 70:
        return "delivered"
    elif bucket < 90:
        return "shadow"
    else:
        return "WITHHELD"

mutants_x_allocate_signal_cohort__mutmut['_mutmut_orig'] = x_allocate_signal_cohort__mutmut_orig # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_1'] = x_allocate_signal_cohort__mutmut_1 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_2'] = x_allocate_signal_cohort__mutmut_2 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_3'] = x_allocate_signal_cohort__mutmut_3 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_4'] = x_allocate_signal_cohort__mutmut_4 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_5'] = x_allocate_signal_cohort__mutmut_5 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_6'] = x_allocate_signal_cohort__mutmut_6 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_7'] = x_allocate_signal_cohort__mutmut_7 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_8'] = x_allocate_signal_cohort__mutmut_8 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_9'] = x_allocate_signal_cohort__mutmut_9 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_10'] = x_allocate_signal_cohort__mutmut_10 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_11'] = x_allocate_signal_cohort__mutmut_11 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_12'] = x_allocate_signal_cohort__mutmut_12 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_13'] = x_allocate_signal_cohort__mutmut_13 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_14'] = x_allocate_signal_cohort__mutmut_14 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_15'] = x_allocate_signal_cohort__mutmut_15 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_16'] = x_allocate_signal_cohort__mutmut_16 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_17'] = x_allocate_signal_cohort__mutmut_17 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_18'] = x_allocate_signal_cohort__mutmut_18 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_19'] = x_allocate_signal_cohort__mutmut_19 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_20'] = x_allocate_signal_cohort__mutmut_20 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_21'] = x_allocate_signal_cohort__mutmut_21 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_22'] = x_allocate_signal_cohort__mutmut_22 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_23'] = x_allocate_signal_cohort__mutmut_23 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_24'] = x_allocate_signal_cohort__mutmut_24 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_25'] = x_allocate_signal_cohort__mutmut_25 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_26'] = x_allocate_signal_cohort__mutmut_26 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_27'] = x_allocate_signal_cohort__mutmut_27 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_28'] = x_allocate_signal_cohort__mutmut_28 # type: ignore # mutmut generated
mutants_x_allocate_signal_cohort__mutmut['x_allocate_signal_cohort__mutmut_29'] = x_allocate_signal_cohort__mutmut_29 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut: MutantDict = {}  # type: ignore

@_mutmut_mutated(mutants_x_build_policy_version_meta__mutmut)
def build_policy_version_meta(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_orig(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_1(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = None
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_2(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(None, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_3(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, None)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_4(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_5(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, )
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_6(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "XXcohortXX": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_7(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "COHORT": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_8(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "XXpolicy_versionsXX": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_9(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "POLICY_VERSIONS": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_10(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "XXscoringXX": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_11(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "SCORING": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_12(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "XXgatesXX": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_13(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "GATES": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_14(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "XXml_modelXX": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_15(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ML_MODEL": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_16(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "XXmeta_label_probabilityXX": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_17(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "META_LABEL_PROBABILITY": meta_prob,
        "allocated_at": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_18(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "XXallocated_atXX": ts.isoformat()
    }

def x_build_policy_version_meta__mutmut_19(ticker: str, ts: datetime, meta_prob: float = None) -> Dict:
    """
    QENG-6c: Construct policy metadata to track causal versions and cohort assignments.
    """
    cohort = allocate_signal_cohort(ticker, ts)
    
    return {
        "cohort": cohort,
        "policy_versions": {
            "scoring": SCORING_POLICY_VERSION,
            "gates": GATES_POLICY_VERSION,
            "ml_model": ML_MODEL_ID
        },
        "meta_label_probability": meta_prob,
        "ALLOCATED_AT": ts.isoformat()
    }

mutants_x_build_policy_version_meta__mutmut['_mutmut_orig'] = x_build_policy_version_meta__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_1'] = x_build_policy_version_meta__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_2'] = x_build_policy_version_meta__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_3'] = x_build_policy_version_meta__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_4'] = x_build_policy_version_meta__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_5'] = x_build_policy_version_meta__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_6'] = x_build_policy_version_meta__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_7'] = x_build_policy_version_meta__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_8'] = x_build_policy_version_meta__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_9'] = x_build_policy_version_meta__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_10'] = x_build_policy_version_meta__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_11'] = x_build_policy_version_meta__mutmut_11 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_12'] = x_build_policy_version_meta__mutmut_12 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_13'] = x_build_policy_version_meta__mutmut_13 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_14'] = x_build_policy_version_meta__mutmut_14 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_15'] = x_build_policy_version_meta__mutmut_15 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_16'] = x_build_policy_version_meta__mutmut_16 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_17'] = x_build_policy_version_meta__mutmut_17 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_18'] = x_build_policy_version_meta__mutmut_18 # type: ignore # mutmut generated
mutants_x_build_policy_version_meta__mutmut['x_build_policy_version_meta__mutmut_19'] = x_build_policy_version_meta__mutmut_19 # type: ignore # mutmut generated
