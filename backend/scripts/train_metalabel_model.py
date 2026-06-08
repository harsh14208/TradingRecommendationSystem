"""
Meta-label model training — Triple Barrier relabeling on backtest trades.

Usage:
    cd backend && python scripts/train_metalabel_model.py
    cd backend && python scripts/train_metalabel_model.py --check    # dry run
    cd backend && python scripts/train_metalabel_model.py --apply    # save model

Pipeline:
  1. Load IS backtest trades CSV produced by backtest_technicals.py.
  2. Relabel each trade with Triple Barrier Method (López de Prado, Ch. 3):
       upper barrier: +2.0×ATR above entry  →  label 1  (target hit first)
       lower barrier: −1.5×ATR below entry  →  label 0  (stop hit first)
       vertical bar:  day-10 close          →  label 1/0 by sign of return
  3. Extract 11-feature meta-label vector (entry_prob is the key feature).
  4. Train XGBoost on triple-barrier labels.
  5. Evaluate with purged expanding-window CV (K=5, embargo=20d).
  6. Save to data/meta_label_model.json + data/meta_label_features.json.

The meta-label model answers: "Given that the primary model says BUY with
this entry_prob, in this macro regime and microstructure context, is the
prediction reliable?"  It does NOT predict direction — only viability.

Minimum training data: 200 resolved IS trades with ATR available.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("train_meta")

_BACKEND = Path(__file__).parent.parent
_DATA_DIR = _BACKEND / "data"
_META_MODEL_FILE = _DATA_DIR / "meta_label_model.json"
_META_FEATURE_FILE = _DATA_DIR / "meta_label_features.json"
_IS_TRADES_FILE = _DATA_DIR / "backtest_trades_is.csv"  # output of backtest_technicals.py --save-trades

# Triple barrier parameters — must match live backtest config
_UPPER_MULT = 2.0  # ×ATR above entry (target)
_LOWER_MULT = 1.5  # ×ATR below entry (stop)
_HOLD_DAYS = 10  # vertical barrier

# Meta-label feature names (must match signal_ml._META_FEATURE_NAMES)
_META_FEATURE_NAMES = [
    "entry_prob",
    "ou_halflife",
    "hurst",
    "vix",
    "atr_pct",
    "rvol",
    "hmm_bull_prob",
    "hmm_trans_risk",
    "dte_bucket",
    "sector_ord",
    "dow",
]

_SECTOR_ORD = {
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


# ── Triple Barrier labeling ───────────────────────────────────────────────────


def apply_triple_barrier(
    trades: pd.DataFrame,
    price_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Relabel each IS backtest trade using the Triple Barrier Method.

    Args:
        trades:     DataFrame with columns: ticker, entry_date, entry_price, atr
        price_data: {ticker: OHLCV DataFrame}

    Returns:
        DataFrame with an additional 'tb_label' column (1=winner, 0=loser).
    """
    labels = []
    for _, row in trades.iterrows():
        ticker = str(row.get("ticker", ""))
        try:
            entry_date = pd.Timestamp(row["entry_date"])
        except Exception:
            labels.append(np.nan)
            continue

        entry_price = float(row.get("entry_price") or 0)
        atr = float(row.get("atr") or 0)
        if entry_price <= 0 or atr <= 0:
            labels.append(np.nan)
            continue

        df_t = price_data.get(ticker)
        if df_t is None or df_t.empty:
            labels.append(np.nan)
            continue

        upper = entry_price * (1 + _UPPER_MULT * atr / entry_price)
        lower = entry_price * (1 - _LOWER_MULT * atr / entry_price)

        # Forward price window: days 1–10 after entry
        try:
            if df_t.index.tz is not None:
                if entry_date.tz is None:
                    entry_date = entry_date.tz_localize("UTC").tz_convert(df_t.index.tz)
                else:
                    entry_date = entry_date.tz_convert(df_t.index.tz)
            else:
                if entry_date.tz is not None:
                    entry_date = entry_date.tz_localize(None)

            idx_pos = df_t.index.searchsorted(entry_date)
            fwd = df_t.iloc[idx_pos + 1 : idx_pos + 1 + _HOLD_DAYS]
        except Exception as e_idx:
            labels.append(np.nan)
            continue

        if fwd.empty:
            labels.append(np.nan)
            continue

        hit_upper = None
        hit_lower = None
        for bar_idx, bar in fwd.iterrows():
            h = float(bar.get("High") or bar.get("high") or 0)
            lo = float(bar.get("Low") or bar.get("low") or 0)
            if h >= upper:
                hit_upper = bar_idx
                break
            if lo <= lower:
                hit_lower = bar_idx
                break

        if hit_upper is not None:
            labels.append(1)
        elif hit_lower is not None:
            labels.append(0)
        else:
            # Vertical barrier: label by sign of day-10 close return
            close_final = float(fwd["Close"].iloc[-1]) if "Close" in fwd.columns else 0
            labels.append(1 if close_final > entry_price else 0)

    trades = trades.copy()
    trades["tb_label"] = labels
    return trades


# ── Feature extraction ────────────────────────────────────────────────────────


def _dte_bucket(dte) -> float:
    if dte is None or (isinstance(dte, float) and np.isnan(dte)):
        return float("nan")
    dte = int(dte)
    if dte < 7:
        return 0.0
    if dte < 35:
        return 1.0
    if dte <= 65:
        return 2.0
    return 3.0


def extract_meta_features(trades: pd.DataFrame) -> np.ndarray:
    """
    Build the 11-feature meta-label matrix from backtest trade columns.
    Uses NaN for missing fields — XGBoost handles NaN natively.
    """
    rows = []
    for _, r in trades.iterrows():
        price = float(r.get("entry_price") or 0)
        atr = float(r.get("atr") or 0)
        atr_pct = (atr / price * 100.0) if price > 0 else float("nan")

        try:
            entry_date = pd.Timestamp(r["entry_date"])
            dow = float(entry_date.weekday())
        except Exception:
            dow = float("nan")

        row = [
            float(r.get("entry_prob") or float("nan")),
            float(r.get("ou_halflife") or float("nan")),
            float(r.get("hurst") or float("nan")),
            float(r.get("vix") or float("nan")),
            atr_pct,
            float(r.get("rvol") or float("nan")),
            float(r.get("hmm_bull_prob") or 0.5),
            float(r.get("hmm_trans_risk") or 0.1),
            _dte_bucket(r.get("days_to_earnings")),
            float(_SECTOR_ORD.get(str(r.get("sector_etf") or ""), -1)),
            dow,
        ]
        rows.append(row)

    return np.array(rows, dtype=float)


# ── Purged CV ─────────────────────────────────────────────────────────────────


def purged_expanding_cv(
    X: np.ndarray,
    y: np.ndarray,
    dates: pd.DatetimeIndex,
    n_splits: int = 5,
    embargo_days: int = 20,
):
    """
    Expanding-window purged cross-validation (López de Prado, Ch. 7).
    Train on first k/n history; test on next split; embargo gap between them.
    Returns list of (train_idx, test_idx) tuples.
    """
    n = len(X)
    fold_size = n // (n_splits + 1)
    splits = []
    for k in range(1, n_splits + 1):
        train_end = k * fold_size
        embargo_end = train_end + embargo_days
        test_start = min(embargo_end, n - 1)
        test_end = min(test_start + fold_size, n)
        if test_start >= n or test_end <= test_start:
            break
        splits.append((np.arange(train_end), np.arange(test_start, test_end)))
    return splits


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Dry run — no model saved")
    parser.add_argument("--apply", action="store_true", help="Save model to data/")
    parser.add_argument(
        "--trades",
        default=str(_IS_TRADES_FILE),
        help="Path to IS trades CSV (default: data/backtest_trades_is.csv)",
    )
    args = parser.parse_args()

    try:
        import xgboost as xgb
    except ImportError:
        log.error("xgboost not installed — run: pip install xgboost")
        sys.exit(1)

    # ── Load trades ───────────────────────────────────────────────────────────
    trades_path = Path(args.trades)
    if not trades_path.exists():
        log.error(
            "Trades file not found: %s\nGenerate it with: python scripts/backtest_technicals.py --save-trades",
            trades_path,
        )
        sys.exit(1)

    date_col = "date" if "date" in pd.read_csv(trades_path, nrows=5).columns else "entry_date"
    trades = pd.read_csv(trades_path, parse_dates=[date_col])
    if date_col == "date":
        trades.rename(columns={"date": "entry_date"}, inplace=True)
    if "entry" in trades.columns and "entry_price" not in trades.columns:
        trades.rename(columns={"entry": "entry_price"}, inplace=True)
    if "atr_pct" in trades.columns and "atr" not in trades.columns:
        trades["atr"] = trades["entry_price"] * trades["atr_pct"] / 100.0

    log.info("Loaded %d IS trades from %s", len(trades), trades_path)

    required_cols = {"ticker", "entry_date", "entry_price", "atr"}
    missing = required_cols - set(trades.columns)
    if missing:
        log.error("Trades CSV missing columns: %s", missing)
        sys.exit(1)

    # ── Triple Barrier relabeling ─────────────────────────────────────────────
    # Load price histories for all tickers in the trade set
    log.info("Loading price histories for %d unique tickers…", trades["ticker"].nunique())

    # Try to import get_history — requires running inside backend/ with venv
    try:
        import asyncio
        import os
        import sys as _sys

        _sys.path.insert(0, str(_BACKEND))
        os.chdir(str(_BACKEND))
        from services.market_data import get_history

        tickers = trades["ticker"].unique().tolist()

        async def _fetch_all():
            tasks = {t: get_history(t, period="max", interval="1d") for t in tickers}
            results = {}
            for t, coro in tasks.items():
                try:
                    results[t] = await coro
                except Exception:
                    results[t] = None
            return results

        price_data = asyncio.run(_fetch_all())
        log.info("Fetched price data for %d tickers", sum(1 for v in price_data.values() if v is not None))
    except Exception as e:
        log.warning("Could not fetch live price data (%s) — using net_pct for labeling", e)
        price_data = {}

    if price_data:
        trades = apply_triple_barrier(trades, price_data)
        valid = trades["tb_label"].notna()
        log.info(
            "Triple-barrier labels: %d valid / %d total  (target=%.0f%%, stop=%.0f%%)",
            valid.sum(),
            len(trades),
            (trades.loc[valid, "tb_label"] == 1).mean() * 100,
            (trades.loc[valid, "tb_label"] == 0).mean() * 100,
        )
        y = trades.loc[valid, "tb_label"].values.astype(int)
        X_all = extract_meta_features(trades[valid])
        dates_all = pd.DatetimeIndex(trades.loc[valid, "entry_date"])
    else:
        # Fallback: use original net_pct label
        log.info("Fallback: using net_pct > 0 as label")
        valid = trades["net_pct"].notna() if "net_pct" in trades.columns else pd.Series(False, index=trades.index)
        if not valid.any():
            log.error("No valid trades with net_pct found — cannot train")
            sys.exit(1)
        y = (trades.loc[valid, "net_pct"] > 0).astype(int).values
        X_all = extract_meta_features(trades[valid])
        dates_all = pd.DatetimeIndex(trades.loc[valid, "entry_date"])

    if len(y) < 200:
        log.warning("Only %d training samples — meta-label model may be unreliable (min 200 recommended)", len(y))

    log.info("Training set: N=%d  pos_rate=%.1f%%", len(y), y.mean() * 100)

    # ── Purged expanding-window CV ────────────────────────────────────────────
    splits = purged_expanding_cv(X_all, y, dates_all, n_splits=5, embargo_days=20)
    cv_aucs = []
    for fold, (train_idx, test_idx) in enumerate(splits, 1):
        X_tr, X_te = X_all[train_idx], X_all[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]
        if len(np.unique(y_tr)) < 2 or len(np.unique(y_te)) < 2:
            continue
        m = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        m.fit(X_tr, y_tr)
        from sklearn.metrics import roc_auc_score

        auc = roc_auc_score(y_te, m.predict_proba(X_te)[:, 1])
        cv_aucs.append(auc)
        log.info("  Fold %d: AUC=%.4f  N_train=%d  N_test=%d", fold, auc, len(train_idx), len(test_idx))

    if cv_aucs:
        log.info(
            "Meta-label CV-AUC: %.4f ± %.4f  (K=%d folds)",
            np.mean(cv_aucs),
            np.std(cv_aucs),
            len(cv_aucs),
        )

    # ── Final model on all data ───────────────────────────────────────────────
    final_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    final_model.fit(X_all, y)
    log.info("Final model trained on N=%d samples", len(y))

    # Feature importance
    importance = dict(zip(_META_FEATURE_NAMES, final_model.feature_importances_))
    for feat, imp in sorted(importance.items(), key=lambda x: -x[1]):
        log.info("  %-20s %.4f", feat, imp)

    if args.check:
        log.info("[--check] Dry run complete — no model saved")
        return

    if args.apply or not args.check:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        booster = final_model.get_booster()
        booster.save_model(str(_META_MODEL_FILE))

        meta = {
            "trained_at": datetime.now().isoformat(),
            "n_train": int(len(y)),
            "pos_rate": round(float(y.mean()), 4),
            "cv_auc_mean": round(float(np.mean(cv_aucs)), 4) if cv_aucs else None,
            "cv_auc_std": round(float(np.std(cv_aucs)), 4) if cv_aucs else None,
            "feature_names": _META_FEATURE_NAMES,
            "feature_importance": {k: round(float(v), 4) for k, v in importance.items()},
            "upper_mult": _UPPER_MULT,
            "lower_mult": _LOWER_MULT,
            "hold_days": _HOLD_DAYS,
        }
        with open(_META_FEATURE_FILE, "w") as f:
            json.dump(meta, f, indent=2)

        log.info("Saved: %s", _META_MODEL_FILE)
        log.info("Saved: %s", _META_FEATURE_FILE)


if __name__ == "__main__":
    main()
