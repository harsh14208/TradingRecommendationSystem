"""§89b: Factor attribution — regress IS trade returns on FF5 + ST_Rev.

Usage:
    cd backend && python scripts/factor_attribution.py

Loads data/backtest_trades_is.csv and joins with FF daily factors
(Fama-French 5-factor + ST_Rev) from Ken French Data Library.
Runs OLS: net_pct = α + β_mkt*MKT-RF + β_smb*SMB + β_hml*HML +
                     β_rmw*RMW + β_cma*CMA + β_str*ST_Rev + ε
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache_ff"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _fetch_ff5_daily() -> pd.DataFrame:
    """Fetch FF5 daily factors + ST_Rev from Ken French."""
    cache = _CACHE_DIR / "ff5_daily.json"
    if cache.exists():
        df = pd.read_json(cache)
        df["date"] = pd.to_datetime(df["date"])
        return df

    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f, skiprows=3)
    df.columns = [c.strip().lower() for c in df.columns]
    # Drop footer rows
    df = df[df.iloc[:, 0].astype(str).str.match(r"^\d{8}$")].copy()
    df["date"] = pd.to_datetime(df.iloc[:, 0].astype(str), format="%Y%m%d")
    # Columns: date, mkt-rf, smb, hml, rmw, cma, rf
    df = df.rename(columns={c: c.replace(" ", "_") for c in df.columns})
    df.to_json(cache, orient="records", date_format="iso")
    return df


def _fetch_str_daily() -> pd.DataFrame:
    """Fetch ST_Rev daily factor."""
    cache = _CACHE_DIR / "str_daily.json"
    if cache.exists():
        df = pd.read_json(cache)
        df["date"] = pd.to_datetime(df["date"])
        return df

    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_ST_Reversal_Factor_daily_CSV.zip"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f, skiprows=13)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df[df.iloc[:, 0].astype(str).str.match(r"^\d{8}$")].copy()
    df["date"] = pd.to_datetime(df.iloc[:, 0].astype(str), format="%Y%m%d")
    df = df.rename(columns={df.columns[1]: "st_rev"})
    df.to_json(cache, orient="records", date_format="iso")
    return df[["date", "st_rev"]]


def main():
    trades_path = Path(__file__).parent.parent / "data" / "backtest_trades_is.csv"
    if not trades_path.exists():
        print(f"> Missing {trades_path} — run backtest first.")
        return

    trades = pd.read_csv(trades_path)
    trades["date"] = pd.to_datetime(trades["date"]).dt.normalize()

    print("Fetching FF5 factors…")
    ff5 = _fetch_ff5_daily()
    print(f"  FF5: {len(ff5)} daily obs")

    print("Fetching ST_Rev factor…")
    str_df = _fetch_str_daily()
    print(f"  ST_Rev: {len(str_df)} daily obs")

    # Merge
    merged = trades.merge(ff5, on="date", how="left").merge(str_df, on="date", how="left")
    merged = merged.dropna(subset=["mkt-rf", "smb", "hml", "rmw", "cma", "st_rev", "net_pct"])
    print(f"\n> {len(merged)}/{len(trades)} trades have factor data\n")

    if len(merged) < 30:
        print("Too few overlapping trades for regression.")
        return

    import statsmodels.api as sm

    X = merged[["mkt-rf", "smb", "hml", "rmw", "cma", "st_rev"]].astype(float)
    X = sm.add_constant(X)
    y = merged["net_pct"].astype(float)

    model = sm.OLS(y, X).fit()
    print(model.summary())

    # Key metrics
    alpha = model.params.get("const", 0)
    alpha_p = model.pvalues.get("const", 1)
    r2 = model.rsquared
    print("\n## Key Results")
    print(f"  Alpha (daily): {alpha:.4f}%  (p={alpha_p:.3f})")
    print(f"  Annualized alpha: {alpha * 252:.2f}%")
    print(f"  R²: {r2:.3f}")
    print(f"  N: {int(model.nobs)}")

    # Decomposition
    factor_contrib = {}
    for col in ["mkt-rf", "smb", "hml", "rmw", "cma", "st_rev"]:
        beta = model.params.get(col, 0)
        mean_factor = merged[col].mean()
        factor_contrib[col] = beta * mean_factor * 252

    print("\n## Annual Return Decomposition")
    print(f"  Alpha:           {alpha * 252:+.2f}%")
    for col, val in factor_contrib.items():
        print(f"  {col.upper():15s} {val:+.2f}%  (β={model.params.get(col, 0):.3f})")
    print("  ─────────────────────────────")
    print(f"  Predicted total: {sum(factor_contrib.values()) + alpha * 252:+.2f}%")
    print(f"  Actual total:    {merged['net_pct'].sum():+.2f}%")


if __name__ == "__main__":
    main()
