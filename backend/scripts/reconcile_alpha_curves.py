"""Reconcile shared-simulator curves against each engine's own curve and report.

Inputs
------
- analysis_output/shared_mr_equity.csv
- analysis_output/shared_futures_equity.csv
- backend/data/mr_monthly_equity.csv (or mr_monthly.csv fallback)
- analysis_output/signal_engine_equity.csv

Outputs
-------
- analysis_output/reconciliation_report.json
- stdout summary table
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "analysis_output"
DATA_DIR = ROOT / "backend" / "data"


def _load_monthly(path: Path, col: str = "net_pct") -> pd.Series:
    df = pd.read_csv(path, index_col=0)
    s = df.iloc[:, 0] if col not in df.columns else df[col]
    s.index = pd.to_datetime(s.index).to_period("M").astype(str)
    return s.rename(col)


def _annualised_sharpe(monthly: pd.Series) -> float:
    m = monthly.dropna()
    if m.std() == 0:
        return 0.0
    return float(m.mean() / m.std() * np.sqrt(12))


def _cagr(monthly: pd.Series) -> float:
    m = monthly.dropna()
    if len(m) == 0:
        return 0.0
    return float((1 + m).prod() ** (12 / len(m)) - 1)


def _max_dd(monthly: pd.Series) -> float:
    eq = (1 + monthly).cumprod()
    return float((eq / eq.cummax() - 1).min())


def reconcile_series(name: str, shared: pd.Series, original: pd.Series) -> dict:
    j = pd.DataFrame({"shared": shared, "original": original}).dropna()
    if len(j) < 6:
        return {
            "name": name,
            "shared_months": len(shared),
            "original_months": len(original),
            "overlap": len(j),
            "error": "too few overlapping months",
        }

    diff = j["shared"] - j["original"]
    return {
        "name": name,
        "shared_months": len(shared),
        "original_months": len(original),
        "overlap": len(j),
        "shared_cagr": round(_cagr(j["shared"]), 4),
        "shared_sharpe": round(_annualised_sharpe(j["shared"]), 3),
        "shared_max_dd": round(_max_dd(j["shared"]), 4),
        "original_cagr": round(_cagr(j["original"]), 4),
        "original_sharpe": round(_annualised_sharpe(j["original"]), 3),
        "original_max_dd": round(_max_dd(j["original"]), 4),
        "corr": round(float(j["shared"].corr(j["original"])), 4),
        "mean_abs_diff_pct": round(float(diff.abs().mean() * 100), 4),
        "max_abs_diff_pct": round(float(diff.abs().max() * 100), 4),
        "first_diff_month": str(j.index[0]) if len(j) else None,
        "last_diff_month": str(j.index[-1]) if len(j) else None,
    }


def main() -> None:
    reports = []
    missing: list[str] = []

    # MR
    shared_mr = OUT_DIR / "shared_mr_equity.csv"
    original_mr = (
        OUT_DIR / "mr_monthly_equity.csv"
        if (OUT_DIR / "mr_monthly_equity.csv").exists()
        else DATA_DIR / "mr_monthly_equity.csv"
    )
    if not original_mr.exists():
        original_mr = DATA_DIR / "mr_monthly.csv"

    if shared_mr.exists() and original_mr.exists():
        reports.append(reconcile_series("MR", _load_monthly(shared_mr), _load_monthly(original_mr)))
    else:
        missing.append(f"MR: missing {shared_mr} or {original_mr}")

    # Futures
    shared_fut = OUT_DIR / "shared_futures_equity.csv"
    original_fut = OUT_DIR / "signal_engine_equity.csv"
    if shared_fut.exists() and original_fut.exists():
        original = pd.read_csv(original_fut, index_col=0, parse_dates=True).iloc[:, 0]
        original_monthly = original.resample("ME").last().pct_change().dropna()
        original_monthly.index = original_monthly.index.to_period("M").astype(str)
        reports.append(reconcile_series("Futures", _load_monthly(shared_fut), original_monthly))
    else:
        missing.append(f"Futures: missing {shared_fut} or {original_fut}")

    # Simple risk-parity blend of shared MR and futures (for diagnostics, not the final §10 blend).
    if shared_mr.exists() and shared_fut.exists():
        mr = _load_monthly(shared_mr)
        fut = _load_monthly(shared_fut)
        j = pd.DataFrame({"mr": mr, "fut": fut}).dropna()
        if len(j) >= 12:
            mr_vol = j["mr"].std()
            fut_vol = j["fut"].std()
            total_vol = mr_vol + fut_vol
            if total_vol > 0:
                w_mr = fut_vol / total_vol
                w_fut = mr_vol / total_vol
            else:
                w_mr = w_fut = 0.5
            blend = w_mr * j["mr"] + w_fut * j["fut"]
            blend_report = {
                "name": "Shared MR+Futures risk-parity blend",
                "overlap": len(j),
                "w_mr": round(w_mr, 4),
                "w_fut": round(w_fut, 4),
                "cagr": round(_cagr(blend), 4),
                "sharpe": round(_annualised_sharpe(blend), 3),
                "max_dd": round(_max_dd(blend), 4),
                "mr_corr": round(j["mr"].corr(j["fut"]), 4),
            }
            reports.append(blend_report)

    report_path = OUT_DIR / "reconciliation_report.json"
    report_path.write_text(json.dumps(reports, indent=2))

    print(json.dumps(reports, indent=2))
    if missing:
        print("\nMissing inputs (skipped):")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
