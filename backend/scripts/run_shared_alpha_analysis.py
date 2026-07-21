"""Run the shared simulator and produce reconciled alpha-blend curves.

Usage:
    .venv311/bin/python backend/scripts/run_shared_alpha_analysis.py

Inputs
------
- backend/data/mr_trades.csv (with entry_date, exit_date, gross_pct, net_pct)
- analysis_output/signal_engine_per_instrument_returns.csv
- analysis_output/signal_engine_equity.csv
- backend/data/mr_monthly_equity.csv (original MR curve)

Outputs
-------
- analysis_output/shared_mr_equity.csv
- analysis_output/shared_futures_equity.csv
- analysis_output/shared_blend_equity.csv
- analysis_output/reconciliation_report.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent.resolve()
BACKEND = HERE.parent
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from scripts.shared_alpha_simulator import simulate_mr_trades, simulate_futures_positions  # noqa: E402

OUT_DIR = ROOT / "analysis_output"
DATA_DIR = BACKEND / "data"


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


def reconcile(name: str, shared: pd.Series, original: pd.Series) -> dict:
    j = pd.DataFrame({"shared": shared, "original": original}).dropna()
    if len(j) < 6:
        return {"name": name, "overlap": len(j), "error": "too few overlapping months"}
    diff = j["shared"] - j["original"]
    return {
        "name": name,
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
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    curves: dict[str, pd.Series] = {}

    # ── MR ──
    mr_csv = DATA_DIR / "mr_trades.csv"
    if mr_csv.exists() and {"entry_date", "exit_date"}.issubset(pd.read_csv(mr_csv).columns):
        trades = pd.read_csv(mr_csv)

        # Isolated exit-date effect: keep every other convention identical to the
        # original engine in backtest_technicals.py.
        #   - net_pct is the engine's net-of-friction return (0.5% round-trip already embedded).
        #   - max_concurrent = 5 == MAX_PORTFOLIO_SLOTS.
        #   - idle cash earns 0% (_T_BILL_ANN = 0.0 in the original engine).
        mr_matched = simulate_mr_trades(trades, max_concurrent=5, friction_pct=0.0, use_gross=False, tbill_rate=0.0)
        mr_matched["monthly"].to_csv(OUT_DIR / "shared_mr_equity.csv", header=["net_pct"])
        curves["MR"] = _load_monthly(OUT_DIR / "shared_mr_equity.csv")
        print(
            f"Shared MR (matched): {len(curves['MR'])} months, "
            f"CAGR {_cagr(curves['MR']):.2%}, Sharpe {_annualised_sharpe(curves['MR']):.3f}, "
            f"MaxDD {_max_dd(curves['MR']):.2%}"
        )

        # Sensitivity diagnostics to decompose the previously confounded changes.
        # These are reported as separate, labelled experiments so the exit-date effect
        # is not mixed up with friction, slot count, or cash yield.
        print("\nMR sensitivity diagnostics (real exits, varying one convention at a time):")
        variants = {
            "gross_minus_0.5_friction": simulate_mr_trades(
                trades, max_concurrent=5, friction_pct=0.5, use_gross=True, tbill_rate=0.0
            ),
            "6_slots": simulate_mr_trades(trades, max_concurrent=6, friction_pct=0.0, use_gross=False, tbill_rate=0.0),
            "4pct_tbill": simulate_mr_trades(
                trades, max_concurrent=5, friction_pct=0.0, use_gross=False, tbill_rate=0.04
            ),
            "zero_friction_gross": simulate_mr_trades(
                trades, max_concurrent=5, friction_pct=0.0, use_gross=True, tbill_rate=0.0
            ),
        }
        for label, res in variants.items():
            m = res["monthly"]
            print(
                f"  {label}: {len(m)} months, "
                f"CAGR {_cagr(m):.2%}, Sharpe {_annualised_sharpe(m):.3f}, MaxDD {_max_dd(m):.2%}"
            )
            reports.append(
                {
                    "name": f"MR sensitivity: {label}",
                    "cagr": round(_cagr(m), 4),
                    "sharpe": round(_annualised_sharpe(m), 3),
                    "max_dd": round(_max_dd(m), 4),
                }
            )

        original_mr = (
            OUT_DIR / "mr_monthly_equity.csv"
            if (OUT_DIR / "mr_monthly_equity.csv").exists()
            else DATA_DIR / "mr_monthly_equity.csv"
        )
        if not original_mr.exists():
            original_mr = DATA_DIR / "mr_monthly.csv"
        if original_mr.exists():
            reports.append(reconcile("MR (real exits, matched conventions)", curves["MR"], _load_monthly(original_mr)))
    else:
        print(f"MR data not ready: {mr_csv}")

    # ── Futures ──
    pir_csv = OUT_DIR / "signal_engine_per_instrument_returns.csv"
    if pir_csv.exists():
        pir = pd.read_csv(pir_csv, index_col=0, parse_dates=True)
        fut_res = simulate_futures_positions(pir, friction_bps=0.0, capital=1.0)
        fut_res["monthly"].to_csv(OUT_DIR / "shared_futures_equity.csv", header=["net_pct"])
        curves["Futures"] = _load_monthly(OUT_DIR / "shared_futures_equity.csv")
        print(
            f"\nShared Futures: {len(curves['Futures'])} months, "
            f"CAGR {_cagr(curves['Futures']):.2%}, Sharpe {_annualised_sharpe(curves['Futures']):.3f}, "
            f"MaxDD {_max_dd(curves['Futures']):.2%}"
        )

        original_fut = pd.read_csv(OUT_DIR / "signal_engine_equity.csv", index_col=0, parse_dates=True).iloc[:, 0]
        original_monthly = original_fut.resample("ME").last().pct_change().dropna()
        original_monthly.index = original_monthly.index.to_period("M").astype(str)
        reports.append(reconcile("Futures", curves["Futures"], original_monthly))
    else:
        print(f"Futures data not ready: {pir_csv}")

    # ── Simple risk-parity blend of shared MR + Futures (diagnostic) ──
    if "MR" in curves and "Futures" in curves:
        j = pd.DataFrame({"mr": curves["MR"], "fut": curves["Futures"]}).dropna()
        if len(j) >= 12:
            total_vol = j["mr"].std() + j["fut"].std()
            w_mr = j["fut"].std() / total_vol if total_vol > 0 else 0.5
            w_fut = 1 - w_mr
            blend = w_mr * j["mr"] + w_fut * j["fut"]
            blend.to_csv(OUT_DIR / "shared_blend_equity.csv", header=["net_pct"])
            print(
                f"\nShared MR+Futures blend (MR={w_mr:.2%}, Futures={w_fut:.2%}): "
                f"{len(blend)} months, CAGR {_cagr(blend):.2%}, Sharpe {_annualised_sharpe(blend):.3f}, "
                f"MaxDD {_max_dd(blend):.2%}, MR-Futures corr {j['mr'].corr(j['fut']):.3f}"
            )
            reports.append(
                {
                    "name": "Shared MR+Futures risk-parity blend",
                    "w_mr": round(w_mr, 4),
                    "w_fut": round(w_fut, 4),
                    "cagr": round(_cagr(blend), 4),
                    "sharpe": round(_annualised_sharpe(blend), 3),
                    "max_dd": round(_max_dd(blend), 4),
                    "mr_fut_corr": round(j["mr"].corr(j["fut"]), 4),
                }
            )

    # ── Internal project four-sleeve blend (diagnostic, NOT the published macro four-sleeve) ──
    # NOTE: This is the project's internal alpha sleeve construction (MR, TS-Momentum,
    # Stat-Arb, Cross-Sectional). It is NOT the same as the published document's
    # macro four-sleeve (equity / gold / bonds / trend). The three non-MR sleeves are
    # still pre-aggregated monthly series; a full raw-trade reconstruction would need
    # entry/exit capture in their respective generators.
    sleeve_files = {
        "MR": "backend/data/mr_monthly_equity.csv",
        "TS-Momentum": "backend/data/tsmom_monthly.csv",
        "Stat-Arb": "backend/data/statarb_monthly_is.csv",
        "Cross-Sectional": "backend/data/cross_sectional_monthly_h63.csv",
    }
    sleeve_monthly = {}
    for name, path in sleeve_files.items():
        p = Path(path)
        if p.exists():
            try:
                sleeve_monthly[name] = _load_monthly(p)
            except Exception as e:
                print(f"  could not load {name}: {e}")

    if len(sleeve_monthly) >= 2:
        j = pd.DataFrame(sleeve_monthly).dropna(how="any")
        if len(j) >= 12:
            # Risk-parity weights (inverse vol)
            vols = j.std()
            inv_vol = 1.0 / vols.replace(0, np.nan)
            weights = (inv_vol / inv_vol.sum()).fillna(1.0 / len(inv_vol))
            blend = (j * weights).sum(axis=1)
            blend.to_csv(OUT_DIR / "shared_four_sleeve_equity.csv", header=["net_pct"])
            print(
                f"\nInternal project four-sleeve blend ({len(j)} months): "
                f"CAGR {_cagr(blend):.2%}, Sharpe {_annualised_sharpe(blend):.3f}, "
                f"MaxDD {_max_dd(blend):.2%}"
            )
            for name, w in weights.items():
                print(f"  {name}: {w:.2%}")
            sleeve_corr = j.corr()
            print(
                f"  avg pairwise corr: {sleeve_corr.values[np.triu_indices_from(sleeve_corr.values, k=1)].mean():.3f}"
            )
            reports.append(
                {
                    "name": "Internal project four-sleeve risk-parity blend (NOT published macro four-sleeve)",
                    "weights": {k: round(v, 4) for k, v in weights.to_dict().items()},
                    "cagr": round(_cagr(blend), 4),
                    "sharpe": round(_annualised_sharpe(blend), 3),
                    "max_dd": round(_max_dd(blend), 4),
                    "avg_pairwise_corr": round(
                        sleeve_corr.values[np.triu_indices_from(sleeve_corr.values, k=1)].mean(), 4
                    ),
                }
            )

    (OUT_DIR / "reconciliation_report.json").write_text(json.dumps(reports, indent=2))
    print(f"\nWrote reconciliation report to {OUT_DIR / 'reconciliation_report.json'}")


if __name__ == "__main__":
    main()
