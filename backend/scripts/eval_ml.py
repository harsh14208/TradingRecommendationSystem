"""
ML Model Evaluation — Signal.Trade XGBoost Confidence Adjustment

Answers the commercial question: does the model actually improve which
signals we trade, or is it just adding noise?

Analyses:
  §1  Overall metrics (accuracy, AUC, Brier score)
  §2  Calibration — model win-prob bucket → actual WR
  §3  Lift table — top/mid/bottom thirds by predicted win prob
  §4  Confidence-band comparison — WR before vs after ML adjustment
  §5  Walk-forward AUC — rolling 3-month train/test windows
  §6  Feature importances (from stored metadata)

Usage:
  cd backend && python scripts/eval_ml.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).parent.parent / "data"
_MODEL_FILE = _DATA_DIR / "signal_ml_model.json"
_FEATURE_FILE = _DATA_DIR / "signal_ml_features.json"


def _load_data():
    import asyncio

    async def _fetch():
        from database import AsyncSessionLocal
        from models import Signal
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            rows = (
                await db.execute(
                    select(
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
                "action": r.action,
                "confidence": r.confidence,
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

    return asyncio.run(_fetch())


def _load_model():
    try:
        import xgboost as xgb
    except ImportError:
        print("xgboost not installed")
        sys.exit(1)

    if not _MODEL_FILE.exists():
        print(f"No model at {_MODEL_FILE} — run train first.")
        sys.exit(1)

    booster = xgb.Booster()
    booster.load_model(str(_MODEL_FILE))
    return booster


def _win(row: dict) -> int:
    action = (row.get("action") or "").upper()
    op = row.get("outcome_pct") or 0
    return 1 if (action == "BUY" and op > 0) or (action == "SELL" and op < 0) else 0


def _predict_all(rows, model):
    import numpy as np
    import xgboost as xgb
    from services.signal_ml import _FEATURE_NAMES, _extract_features

    X = [_extract_features(r) for r in rows]
    dm = xgb.DMatrix(np.array(X, dtype=float), feature_names=_FEATURE_NAMES)
    return model.predict(dm).tolist()


def _adjusted_confidence(row, win_prob):
    base_conf = float(row.get("confidence") or 0)
    base_win_prob = base_conf / 100.0 * 0.85
    ratio = win_prob / max(base_win_prob, 0.01)
    ratio = max(0.75, min(1.25, ratio))
    return round(min(72.0, base_conf * ratio), 1)


def _hr(n=72):
    print("─" * n)


# ─────────────────────────────────────────────────────────────────────────────
# Entry-model helpers (§7)
# ─────────────────────────────────────────────────────────────────────────────

_ENTRY_META_FILE = _DATA_DIR / "backtest_ml_features.json"
_ENTRY_EVAL_FILE = _DATA_DIR / "backtest_ml_eval.json"


def shap_audit(rows, model):
    """§7 SHAP Feature Audit — TreeExplainer-based mean |SHAP| per feature.

    Requires `shap` package (pip install shap>=0.45.0).

    Prints:
      - Mean |SHAP| per feature (absolute importance)
      - Direction: whether high feature value → higher win-prob (pos) or lower (neg)
      - Flags features where SHAP direction contradicts expectation (potential inversion)

    Usage: called from main() as §7.
    """
    try:
        import numpy as np
        import shap
        from services.signal_ml import _FEATURE_NAMES, _extract_features
    except ImportError as e:
        print(f"§7 SHAP skipped: {e}")
        return

    print("## §7  SHAP Feature Audit — TreeExplainer\n")
    print("> Mean |SHAP| measures each feature's average contribution to the prediction.")
    print("> Direction: Pos = higher value → higher win-prob; Neg = higher value → lower win-prob.")
    print("> ⚠ flag: SHAP direction contradicts intuition — potential inverted or noisy feature.\n")

    X = np.array([_extract_features(r) for r in rows], dtype=float)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Mean absolute SHAP per feature
    mean_abs = np.abs(shap_values).mean(axis=0)
    # Direction: positive = feature pushes prediction up on average
    mean_shap = shap_values.mean(axis=0)

    ranked = sorted(
        zip(_FEATURE_NAMES, mean_abs, mean_shap),
        key=lambda x: -x[1],
    )

    print("| Rank | Feature | Mean |SHAP| | Direction | Flag |")
    print("|:---|:---|---:|:---:|:---|")

    EXPECTED_POS = {
        "confidence",
        "n_sources",
        "rr",
        "payoff",
        "has_technical",
        "has_options",
        "has_fundamentals",
        "sector_ord",
        "rs_vs_sector",
    }
    EXPECTED_NEG = {
        "dte_bucket",  # lower DTE = worse (earnings risk)
        "change_pct",  # stock already down = higher fear
    }

    for rank, (feat, abs_val, dir_val) in enumerate(ranked[:20], 1):
        direction = "pos ▲" if dir_val > 0 else "neg ▼"
        flag = ""
        if feat in EXPECTED_POS and dir_val < -0.001 or feat in EXPECTED_NEG and dir_val > 0.001:
            flag = "⚠ inverted"
        bar = "█" * int(abs_val * 300)
        print(f"| {rank} | `{feat}` | {abs_val:.5f} {bar} | {direction} | {flag} |")

    print()

    # Summary: features with near-zero SHAP (candidates for removal)
    zero_thresh = 0.001
    noise_feats = [f for f, a, _ in ranked if a < zero_thresh]
    if noise_feats:
        print(f"**Near-zero SHAP features** (mean |SHAP| < {zero_thresh}) — consider dropping:")
        for f in noise_feats:
            print(f"  - `{f}`")
    print()


def main():
    print("\n# XGBoost Model Evaluation — Signal.Trade\n")

    rows = _load_data()
    model = _load_model()
    print(f"Loaded {len(rows)} resolved signals.\n")

    labels = [_win(r) for r in rows]
    probs = _predict_all(rows, model)

    # ── §1  Overall metrics (full + OOS-only) ────────────────────────────────
    try:
        from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score

        # OOS slice: last 30% by time (same split as training)
        split = int(len(rows) * 0.70)
        oos_labels = labels[split:]
        oos_probs = probs[split:]

        preds = [1 if p >= 0.5 else 0 for p in probs]
        oos_preds = [1 if p >= 0.5 else 0 for p in oos_probs]

        acc_full = accuracy_score(labels, preds)
        auc_full = roc_auc_score(labels, probs) if len(set(labels)) > 1 else None
        brier_full = brier_score_loss(labels, probs)

        acc_oos = accuracy_score(oos_labels, oos_preds)
        auc_oos = roc_auc_score(oos_labels, oos_probs) if len(set(oos_labels)) > 1 else None
        brier_oos = brier_score_loss(oos_labels, oos_probs)

        print("## §1  Overall Metrics\n")
        print("> ⚠ Full-dataset numbers include the training set — AUC/accuracy are inflated.")
        print("> OOS column (last 30% by time) is the honest estimate.\n")
        print("| Metric | Full dataset ⚠ | OOS only ✅ |")
        print("|:---|---:|---:|")
        print(f"| N signals | {len(rows)} | {len(oos_labels)} |")
        print(f"| Accuracy | {acc_full:.3f} | {acc_oos:.3f} |")
        print(f"| AUC | {f'{auc_full:.4f}' if auc_full else '—'} | {f'{auc_oos:.4f}' if auc_oos else '—'} |")
        print(f"| Brier score | {brier_full:.4f} | {brier_oos:.4f} |")
        print(f"| Actual WR | {sum(labels) / len(labels):.3f} | {sum(oos_labels) / len(oos_labels):.3f} |")
        print()
    except ImportError:
        print("scikit-learn not installed — skipping §1")
        split = int(len(rows) * 0.70)
        oos_labels = labels[split:]
        oos_probs = probs[split:]

    # ── §2  Calibration ───────────────────────────────────────────────────────
    print("## §2  Calibration — Model Win-Prob Bucket → Actual Win Rate\n")
    print("> If well-calibrated: 0.5–0.6 bucket should have ~55% actual WR, etc.")
    print()

    buckets = [(i / 10, (i + 1) / 10) for i in range(3, 10)]  # 0.3–1.0 in 0.1 steps
    print("| Prob Bucket | N | Actual WR | Model Avg Prob | Gap |")
    print("|:---|---:|---:|---:|---:|")
    for lo, hi in buckets:
        idxs = [i for i, p in enumerate(probs) if lo <= p < hi]
        if not idxs:
            continue
        actual_wr = sum(labels[i] for i in idxs) / len(idxs)
        avg_prob = sum(probs[i] for i in idxs) / len(idxs)
        gap = actual_wr - avg_prob
        bar = "✅" if abs(gap) < 0.08 else ("⬆" if gap > 0 else "⬇")
        print(f"| {lo:.1f}–{hi:.1f} | {len(idxs)} | {actual_wr:.3f} | {avg_prob:.3f} | {gap:+.3f} {bar} |")
    print()

    # ── §3  Lift table ────────────────────────────────────────────────────────
    print("## §3  Lift Table — Top/Mid/Bottom Thirds by Predicted Win Prob\n")
    print("> Strong model: top-third WR >> bottom-third WR.")
    print()

    sorted_idx = sorted(range(len(probs)), key=lambda i: probs[i])
    n = len(sorted_idx)
    thirds = [
        ("Bottom ⅓ (lowest prob)", sorted_idx[: n // 3]),
        ("Mid ⅓", sorted_idx[n // 3 : 2 * n // 3]),
        ("Top ⅓ (highest prob)", sorted_idx[2 * n // 3 :]),
    ]

    print("| Tier | N | WR | Avg Model Prob | Avg Outcome % |")
    print("|:---|---:|---:|---:|---:|")
    for name, idxs in thirds:
        wr = sum(labels[i] for i in idxs) / len(idxs)
        prob = sum(probs[i] for i in idxs) / len(idxs)
        avg_ret = sum((rows[i].get("outcome_pct") or 0) for i in idxs) / len(idxs)
        print(f"| {name} | {len(idxs)} | {wr:.3f} | {prob:.3f} | {avg_ret:+.2f}% |")
    print()

    # ── §4  Confidence-band comparison ────────────────────────────────────────
    print("## §4  Confidence-Band Comparison — WR Before vs After ML Adjustment\n")
    print("> Does the model improve or degrade the deterministic Platt score?")
    print()

    adj_confs = [_adjusted_confidence(rows[i], probs[i]) for i in range(len(rows))]

    bands = [(55, 60), (60, 65), (65, 70), (70, 100)]
    print("| Raw Conf Band | N (raw) | WR (raw) | Avg Adj Conf | WR (adj signals) |")
    print("|:---|---:|---:|---:|---:|")
    for lo, hi in bands:
        # signals in raw band
        idxs = [i for i, r in enumerate(rows) if lo <= (r.get("confidence") or 0) < hi]
        if not idxs:
            continue
        wr_raw = sum(labels[i] for i in idxs) / len(idxs)
        avg_adj = sum(adj_confs[i] for i in idxs) / len(idxs)
        # signals that the model would pass (adj_conf still >= 57 — live min floor)
        passed = [i for i in idxs if adj_confs[i] >= 57.0]
        wr_adj = sum(labels[i] for i in passed) / len(passed) if passed else float("nan")
        print(f"| {lo}–{hi}% | {len(idxs)} | {wr_raw:.3f} | {avg_adj:.1f}% | {wr_adj:.3f} ({len(passed)} signals) |")
    print()

    # ── §5  Walk-forward AUC ─────────────────────────────────────────────────
    print("## §5  Walk-Forward AUC — 3-Month Rolling Windows\n")
    print("> Stable AUC across windows = model generalises; declining = overfit or regime shift.")
    print()

    from datetime import datetime, timedelta

    dated = [(r, labels[i], probs[i]) for i, r in enumerate(rows) if r.get("created_at")]
    dated.sort(key=lambda x: x[0]["created_at"])

    try:
        from sklearn.metrics import roc_auc_score as _auc

        # Find date range
        dates = [datetime.fromisoformat(x[0]["created_at"][:19]) for x in dated]
        start = dates[0]
        end = dates[-1]

        print("| Window | N test | AUC | WR |")
        print("|:---|---:|---:|---:|")

        window_days = 90
        step_days = 30
        cur = start + timedelta(days=window_days)
        while cur <= end + timedelta(days=step_days):
            test_mask = [start + timedelta(days=window_days) <= d < cur + timedelta(days=step_days) for d in dates]
            test_rows = [(x[1], x[2]) for x, m in zip(dated, test_mask) if m]
            if len(test_rows) < 10:
                cur += timedelta(days=step_days)
                continue
            yt = [t[0] for t in test_rows]
            yp = [t[1] for t in test_rows]
            try:
                auc_w = _auc(yt, yp) if len(set(yt)) > 1 else None
            except Exception:
                auc_w = None
            wr_w = sum(yt) / len(yt)
            label = f"{(cur - timedelta(days=step_days)).strftime('%Y-%m')}→{cur.strftime('%Y-%m')}"
            print(f"| {label} | {len(test_rows)} | {auc_w:.3f if auc_w else '—'} | {wr_w:.3f} |")
            cur += timedelta(days=step_days)
        print()
    except Exception as e:
        print(f"Walk-forward skipped: {e}\n")

    # ── §6  Feature importances ───────────────────────────────────────────────
    print("## §6  Feature Importances (from last training run)\n")
    if _FEATURE_FILE.exists():
        meta = json.loads(_FEATURE_FILE.read_text())
        fi = meta.get("feature_importances", [])
        if fi:
            print("| Rank | Feature | Importance |")
            print("|:---|:---|---:|")
            for rank, f in enumerate(fi[:10], 1):
                bar = "█" * int(f["importance"] * 200)
                print(f"| {rank} | {f['feature']} | {f['importance']:.5f} {bar} |")
        print()
        print(f"Trained at: {meta.get('trained_at', '—')}")
        print(f"N train/test: {meta.get('n_train')} / {meta.get('n_test')}")
        print(f"OOS AUC: {meta.get('oos_auc')}  |  Deployed: {meta.get('deployed')}")
    print()

    # ── §7  SHAP audit ────────────────────────────────────────────────────────
    shap_audit(rows, model)

    # ── §8  Entry Model — Backtest XGBoost ───────────────────────────────────
    print("## §8  Entry Model — Backtest XGBoost (23-year IS)\n")
    print("> Trained on IS backtest trade outcomes. OOS = last 30% by trade-date order.")
    print("> Complements signal model: entry model ← technical setup quality;")
    print("> signal model ← signal assembly quality. Blended 50/50 in _assemble_signal().")
    print()

    if not _ENTRY_META_FILE.exists():
        print("No entry model found. Run `python scripts/train_backtest_ml.py` first.\n")
    else:
        _emeta = json.loads(_ENTRY_META_FILE.read_text())
        _oos_auc = _emeta.get("oos_auc")
        print("| Metric | Value |")
        print("|:---|---:|")
        print(f"| Trained at | {str(_emeta.get('trained_at', '—'))[:19]} |")
        print(f"| N train | {_emeta.get('n_train', '—')} |")
        print(f"| N test (OOS) | {_emeta.get('n_test', '—')} |")
        print(f"| OOS AUC | {f'{_oos_auc:.4f}' if _oos_auc else '—'} |")
        print(f"| Deployed | {'✅ Yes' if _emeta.get('deployed') else '⛔ No'} |")
        print()

        _efi = _emeta.get("feature_importances", [])
        if _efi:
            print("### Feature Importances\n")
            print("| Rank | Feature | Importance |")
            print("|:---|:---|---:|")
            for _rank, _f in enumerate(_efi[:10], 1):
                _bar = "█" * int(_f["importance"] * 200)
                print(f"| {_rank} | {_f['feature']} | {_f['importance']:.5f} {_bar} |")
            print()

        if _ENTRY_EVAL_FILE.exists():
            _edata = json.loads(_ENTRY_EVAL_FILE.read_text())
            _yt = _edata.get("y_test", [])
            _yp = _edata.get("oos_preds", [])

            if _yt and _yp:
                print("### Calibration (OOS)\n")
                print("> 0.5–0.6 bucket should have ~55% actual WR if well-calibrated.")
                print()
                print("| Prob Bucket | N | Actual WR | Avg Prob | Gap |")
                print("|:---|---:|---:|---:|---:|")
                for _lo, _hi in [(i / 10, (i + 1) / 10) for i in range(3, 10)]:
                    _idxs = [i for i, p in enumerate(_yp) if _lo <= p < _hi]
                    if not _idxs:
                        continue
                    _awr = sum(_yt[i] for i in _idxs) / len(_idxs)
                    _aprb = sum(_yp[i] for i in _idxs) / len(_idxs)
                    _gap = _awr - _aprb
                    _flg = "✅" if abs(_gap) < 0.10 else ("⬆" if _gap > 0 else "⬇")
                    print(f"| {_lo:.1f}–{_hi:.1f} | {len(_idxs)} | {_awr:.3f} | {_aprb:.3f} | {_gap:+.3f} {_flg} |")
                print()

                print("### Lift Table (OOS)\n")
                print("> Strong model: top-third WR >> bottom-third WR.")
                print()
                _sidx = sorted(range(len(_yp)), key=lambda i: _yp[i])
                _n = len(_sidx)
                print("| Tier | N | WR | Avg Model Prob |")
                print("|:---|---:|---:|---:|")
                for _tname, _tidxs in [
                    ("Bottom ⅓ (lowest prob)", _sidx[: _n // 3]),
                    ("Mid ⅓", _sidx[_n // 3 : 2 * _n // 3]),
                    ("Top ⅓ (highest prob)", _sidx[2 * _n // 3 :]),
                ]:
                    _twr = sum(_yt[i] for i in _tidxs) / len(_tidxs)
                    _tprb = sum(_yp[i] for i in _tidxs) / len(_tidxs)
                    print(f"| {_tname} | {len(_tidxs)} | {_twr:.3f} | {_tprb:.3f} |")
                print()
        else:
            print("> ℹ Calibration/lift unavailable — run `python scripts/train_backtest_ml.py`")
            print("> to regenerate and save eval data to `data/backtest_ml_eval.json`.\n")


if __name__ == "__main__":
    main()
