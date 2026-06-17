"""Generate a continuous MR monthly equity series from the existing mr_trades.csv.

The legacy ``data/mr_monthly.csv`` is a *sparse* average-net-pct-per-trade-month
series, which produces noisy / misleading correlations when blended with the
quarterly-rebalanced cross-sectional model.  This script reconstructs a
month-end equity curve using the same concurrent-slot portfolio simulation as
``backtest_technicals.py::run_portfolio_simulation``.  It is intended to be run
after a fresh ``backtest_technicals.py`` pass so that ``data/mr_trades.csv`` is
current; if ``exit_day`` is absent from the CSV, a conservative synthetic
``exit_day`` is imputed.

Usage:
    cd backend && python scripts/generate_mr_equity_series.py
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(_HERE)
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

import pandas as pd

from scripts.backtest_technicals import run_portfolio_simulation, MAX_PORTFOLIO_SLOTS

_TRADES_CSV = os.path.join(_BACKEND, "data", "mr_trades.csv")
_OUTPUT_CSV = os.path.join(_BACKEND, "data", "mr_monthly_equity.csv")


def main() -> None:
    if not os.path.exists(_TRADES_CSV):
        raise SystemExit(f"Missing {_TRADES_CSV} — run scripts/backtest_technicals.py first.")

    trades = pd.read_csv(_TRADES_CSV)
    required = {"date", "net_pct"}
    if not required.issubset(trades.columns):
        raise SystemExit(f"trades CSV must contain {required}, got {trades.columns.tolist()}")

    # The legacy mr_trades.csv dump does not include exit_day.  Impute a
    # conservative mean hold that mirrors the live MR engine's ATR-based swing
    # exits (bulk of exits occur in the first few trading days; max hold 10).
    if "exit_day" not in trades.columns:
        trades["exit_day"] = 4  # trading days

    res = run_portfolio_simulation(trades, max_concurrent=MAX_PORTFOLIO_SLOTS, quiet=True)
    if not res or not res.get("equity_log"):
        raise SystemExit("Portfolio simulation produced no equity log.")

    eq_df = pd.DataFrame(res["equity_log"], columns=["date", "equity"])
    eq_df["date"] = pd.to_datetime(eq_df["date"])
    me = eq_df.set_index("date").resample("ME").last()
    monthly = me.pct_change().dropna()
    monthly.index = monthly.index.to_period("M").astype(str)
    monthly.to_csv(_OUTPUT_CSV, header=["net_pct"])
    print(f"Wrote continuous MR monthly equity series ({len(monthly)} months) → {_OUTPUT_CSV}")


if __name__ == "__main__":
    main()
