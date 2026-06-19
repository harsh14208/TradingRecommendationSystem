#!/usr/bin/env python3
"""§MASSIVE-1 — Audit Massive vs ORATS implied-vol agreement on 2026 overlap.

Loads the ORATS panel from Postgres and the local Massive-built panel, merges on
(ticker, date), and reports correlations for the IV features the VRP model actually
uses. If `atm_iv_30d` correlation is > 0.9, Massive is a viable replacement for the
live ORATS feed; if lower, ORATS wins on surface quality.

Usage:
    cd backend
    python scripts/audit_massive_orats_iv_agreement.py \
        --massive data/cache_massive/massive_panel_2y.parquet
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from services.orats_data import load_orats_panel_from_db  # noqa: E402


def _corr(a: pd.Series, b: pd.Series) -> float | None:
    mask = a.notna() & b.notna()
    n = mask.sum()
    if n < 10:
        return None
    return float(a[mask].corr(b[mask]))


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit Massive vs ORATS IV agreement")
    ap.add_argument(
        "--massive",
        default="data/cache_massive/massive_panel_2y.parquet",
        help="Path to Massive-built parquet panel",
    )
    ap.add_argument("--min-pairs", type=int, default=10, help="Min (ticker,date) pairs for per-ticker stats")
    args = ap.parse_args()

    massive_path = Path(args.massive)
    if not massive_path.exists():
        print(f"Massive panel not found: {massive_path}")
        print("Build it first with scripts/massive_spike_backtest.py or build_massive_options_panel.py")
        sys.exit(1)

    print("Loading ORATS panel from Postgres…")
    orats_df = asyncio.run(load_orats_panel_from_db())
    if orats_df is None or orats_df.empty:
        print("No ORATS data in DB.")
        sys.exit(1)
    for c in ("date", "effective_date"):
        if c in orats_df.columns:
            orats_df[c] = pd.to_datetime(orats_df[c]).dt.date
    orats = orats_df.rename(
        columns={
            "orats_atm_iv_30d": "atm_iv_30d",
            "orats_pc_iv_skew": "pc_iv_skew",
            "orats_iv_rank": "iv_rank",
            "orats_zero_dte_put_volume": "zero_dte_put_volume",
        }
    )
    orats["date"] = pd.to_datetime(orats["date"]).dt.date

    print(f"Loading Massive panel from {massive_path}…")
    massive = pd.read_parquet(massive_path)
    massive["date"] = pd.to_datetime(massive["date"]).dt.date

    print(f"ORATS:   {len(orats):,} rows, {orats['ticker'].nunique():,} tickers, {orats['date'].nunique()} dates")
    print(
        f"Massive: {len(massive):,} rows, {massive['ticker'].nunique():,} tickers, "
        f"{massive['date'].nunique()} dates ({massive['date'].min()} → {massive['date'].max()})"
    )

    merged = pd.merge(
        orats[["ticker", "date", "atm_iv_30d", "pc_iv_skew"]],
        massive[["ticker", "date", "atm_iv_30d", "pc_iv_skew"]],
        on=["ticker", "date"],
        suffixes=("_orats", "_massive"),
        how="inner",
    )
    print(f"\nOverlap: {len(merged):,} (ticker,date) pairs, {merged['ticker'].nunique():,} tickers")

    if merged.empty:
        print("No overlap — cannot compute agreement.")
        sys.exit(1)

    print("\nOverall correlations (Pearson):")
    for feat in ["atm_iv_30d", "pc_iv_skew"]:
        c = _corr(merged[f"{feat}_orats"], merged[f"{feat}_massive"])
        print(f"  {feat:<16} r = {c:.4f}" if c is not None else f"  {feat:<16} r = —")

    print(f"\nPer-ticker atm_iv_30d correlation (tickers with ≥{args.min_pairs} pairs):")
    per_ticker: list[tuple[str, float, int]] = []
    for t, g in merged.groupby("ticker"):
        if len(g) < args.min_pairs:
            continue
        r = _corr(g["atm_iv_30d_orats"], g["atm_iv_30d_massive"])
        if r is not None:
            per_ticker.append((t, r, len(g)))
    per_ticker.sort(key=lambda x: x[1], reverse=True)
    for t, r, n in per_ticker[:10]:
        print(f"  {t:<6} r={r:+.3f}  n={n}")
    print(
        f"  ... median per-ticker r = {np.median([x[1] for x in per_ticker]):.3f}, "
        f"mean = {np.mean([x[1] for x in per_ticker]):.3f}, "
        f"tickers = {len(per_ticker)}"
    )
    print("\nBottom 5:")
    for t, r, n in per_ticker[-5:]:
        print(f"  {t:<6} r={r:+.3f}  n={n}")

    # IV-level errors
    merged["iv_abs_err"] = (merged["atm_iv_30d_orats"] - merged["atm_iv_30d_massive"]).abs()
    merged["iv_pct_err"] = merged["iv_abs_err"] / merged["atm_iv_30d_orats"]
    print("\nIV level errors:")
    print(f"  mean abs error  = {merged['iv_abs_err'].mean():.4f}")
    print(f"  median abs error= {merged['iv_abs_err'].median():.4f}")
    print(f"  mean pct error  = {merged['iv_pct_err'].mean():.2%}")
    print(f"  median pct error= {merged['iv_pct_err'].median():.2%}")

    out = Path("data/cache_massive/massive_orats_iv_agreement.csv")
    merged[
        ["ticker", "date", "atm_iv_30d_orats", "atm_iv_30d_massive", "pc_iv_skew_orats", "pc_iv_skew_massive"]
    ].to_csv(out, index=False)
    print(f"\nSaved overlap detail to {out}")


if __name__ == "__main__":
    main()
