#!/usr/bin/env python3
"""§111 — ORATS options-gate sensitivity analysis.

Runs the MR-only backtest once across the full universe, then recomputes
metrics under several ORATS feature filters.  The filters are only applied
to trades that have ORATS data (currently 2026); pre-2026 trades are always
kept because there is no point-in-time options history for them.

Usage:
    cd backend && python scripts/analyze_orats_gates.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import scripts.backtest_technicals as bt
from services.orats_data import load_orats_panel_from_db


def _pct(x: float | None) -> str:
    return f"{x * 100:.1f}%" if x is not None else "—"


def _fmt(x: float | None) -> str:
    return f"{x:.3f}" if x is not None else "—"


def _load_macro_inputs() -> tuple[dict, dict, dict]:
    vix_df = bt.cached_yf_download("^VIX", start=bt.START, end=bt.END, interval="1d", auto_adjust=False, progress=False)
    if isinstance(vix_df.columns, pd.MultiIndex):
        vix_df.columns = vix_df.columns.get_level_values(0)
    vix_series = vix_df["Close"] if "Close" in vix_df.columns else pd.Series(dtype=float)
    vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vix_series.items() if pd.notna(v)}

    spy_trend = bt.fetch_spy_trend(bt.START, bt.END)

    _fred_key = ""
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    try:
        with open(_env_path) as _ef:
            for line in _ef:
                if line.startswith("FRED_API_KEY="):
                    _fred_key = line.strip().split("=", 1)[1]
    except Exception:
        pass
    stlfsi4 = bt.fetch_stlfsi4(bt.START, bt.END, _fred_key)
    return vix, spy_trend, stlfsi4


def _load_orats_panel() -> pd.DataFrame | None:
    df = asyncio.run(load_orats_panel_from_db())
    if df is None or df.empty:
        return None
    panel = df.copy()
    for _dcol in ("date", "effective_date"):
        if _dcol in panel.columns:
            panel[_dcol] = pd.to_datetime(panel[_dcol]).dt.date
    bt._alt_data_panels["orats"] = {
        _t: _grp.set_index("date" if "date" in _grp.columns else "effective_date").to_dict("index")
        for _t, _grp in panel.groupby("ticker")
    }
    return df


def _run_backtest(vix: dict, spy_trend: dict, stlfsi4: dict) -> pd.DataFrame:
    args_list = [
        (
            t,
            vix,
            spy_trend,
            stlfsi4,
            True,  # mr_only
            False,  # beta_hedge
            None,  # spy_prices
            False,  # forecast_sizing
            False,  # no_family_discount
        )
        for t in bt.TICKERS
    ]
    all_trades: list[pd.DataFrame] = []
    for args in args_list:
        result = bt.process_ticker(args)
        ticker, _, df, earnings_dates = result
        if df is None:
            continue
        trades = bt.simulate_ticker(ticker, df, vix, spy_trend, stlfsi4, mr_only=True, earnings_dates=earnings_dates)
        if trades is not None and not trades.empty:
            all_trades.append(trades)
    return pd.concat(all_trades, ignore_index=True)


def _metrics(trades: pd.DataFrame, weight_col: str | None = None) -> dict:
    """Compute metrics matching the convention used in backtest_technicals.py."""
    if trades.empty:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None, "max_dd": 0.0}
    trades = trades.sort_values("date") if "date" in trades.columns else trades
    rets = trades["net_pct"].astype(float).to_numpy()
    weights = (
        trades[weight_col].astype(float).to_numpy()
        if weight_col and weight_col in trades.columns
        else np.ones(len(rets))
    )
    # Normalize weights to mean 1.0 (matches backtest weighted-stats convention)
    w_mean = weights.mean()
    if w_mean > 0:
        weights = weights / w_mean
    else:
        weights = np.ones(len(rets))

    weighted_rets = rets * weights
    avg = float(weighted_rets.sum() / weights.sum())
    wr = float((weighted_rets > 0).sum()) / len(weighted_rets)
    std = float(rets.std(ddof=1)) if len(rets) > 1 else 0.0
    # Per-trade Sharpe (not annualized), matching backtest_technicals.py
    sharpe = round(avg / std, 4) if std > 0 and len(rets) >= 10 else None

    # Max drawdown on equity curve using 5% position size
    cap, peak, max_dd = 10_000.0, 10_000.0, 0.0
    for r in weighted_rets:
        cap += cap * bt.POSITION_SIZE * (r / 100)
        peak = max(peak, cap)
        max_dd = max(max_dd, (peak - cap) / peak * 100)
    return {"n": len(rets), "wr": wr, "avg": avg, "sharpe": sharpe, "max_dd": max_dd}


def _print_row(label: str, m: dict) -> None:
    max_dd_str = f"-{m['max_dd']:.2f}%"
    print(
        f"| {label:<30} | {m['n']:>4} | {_pct(m['wr']):>7} | {_fmt(m['avg']):>7} | {_fmt(m['sharpe']):>7} | {max_dd_str:>8} |"
    )


def main() -> None:
    print("Loading ORATS panel from Postgres…")
    orats_df = _load_orats_panel()
    if orats_df is None:
        print("No ORATS data in DB. Run build_orats_panel.py --save-to-db first.")
        sys.exit(1)
    print(f"  → {len(orats_df):,} rows, {orats_df['date'].nunique()} dates, {orats_df['ticker'].nunique()} tickers\n")

    print("Loading macro inputs…")
    vix, spy_trend, stlfsi4 = _load_macro_inputs()
    print(f"  → VIX {len(vix)} bars, SPY trend {len(spy_trend)} bars, STLFSI4 {len(stlfsi4)} bars\n")

    print(f"Running MR-only backtest for {len(bt.TICKERS)} tickers (sequential)…")
    trades = _run_backtest(vix, spy_trend, stlfsi4)
    print(f"  → {len(trades)} raw trades\n")

    # Add an "has_orats" flag: trades with any ORATS feature populated
    trades["has_orats"] = trades["orats_iv_rank"].notna() | trades["orats_pc_iv_skew"].notna()

    print("=" * 90)
    print("ORATS options-gate sensitivity (filters apply only to 2026 trades with ORATS data)")
    print("=" * 90)
    print(f"| {'Variant':<30} | {'N':>4} | {'WR':>7} | {'Avg%':>7} | {'Sharpe':>7} | {'MaxDD':>8} |")
    print("-" * 90)

    # Baseline equal-weight and ORATS-tilt weighted
    _print_row("Baseline equal-weight", _metrics(trades))
    _print_row("ORATS tilt weighted", _metrics(trades, weight_col="size_mult"))

    # Helper: apply a gate only to rows that have ORATS data
    def _gate(mask: pd.Series) -> pd.DataFrame:
        return trades[~trades["has_orats"] | mask]

    _print_row("IV rank >= 50", _metrics(_gate(trades["orats_iv_rank"] >= 50)))
    _print_row("Put skew > 0.10", _metrics(_gate(trades["orats_pc_iv_skew"] > 0.10)))
    _print_row("GEX > 0", _metrics(_gate(trades["orats_gex"] > 0)))
    _print_row(
        "0-DTE puts > 1k & PC vol >1.5",
        _metrics(_gate((trades["orats_zero_dte_put_volume"] > 1000) & (trades["orats_pc_volume_ratio"] > 1.5))),
    )
    _print_row(
        "All four gates combined",
        _metrics(
            _gate(
                (trades["orats_iv_rank"] >= 50)
                & (trades["orats_pc_iv_skew"] > 0.10)
                & (trades["orats_gex"] > 0)
                & (trades["orats_zero_dte_put_volume"] > 1000)
                & (trades["orats_pc_volume_ratio"] > 1.5)
            )
        ),
    )

    print("\nNotes:")
    print("  • 'ORATS tilt weighted' uses the size_mult already applied by --orats (IV rank/skew/GEX/0-DTE).")
    print("  • Gate variants keep all pre-2026 trades and only filter 2026 trades missing the signal.")
    print("  • iv_rank is NaN for early 2026 until ≥60 days of ORATS history accumulate per ticker.")


if __name__ == "__main__":
    main()
