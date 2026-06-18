"""Backtest the residual-cash overlay strategy against the baseline MR engine.

Compares:
  1. Baseline MR (5 slots × 20%, idle cash earns T-bills)
  2. MR + residual SPY overlay (idle cash tracks SPY)
  3. MR + VIX-conditioned SPY overlay (SPY only when prior-day VIX ≤ threshold)

Usage:
    cd backend && python scripts/backtest_overlay.py
    cd backend && python scripts/backtest_overlay.py --max-slots 5 --hold-days 3
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.abspath(os.path.join(_HERE, ".."))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

_T_BILL_ANN = 0.035  # matches scripts/backtest_technicals.py baseline
_CACHE_DIR = os.path.join(_BACKEND, "data", "cache_ohlcv")


def _norm_ticker(ticker: str) -> str:
    return ticker.replace(".", "-")


def load_cached(ticker: str) -> pd.DataFrame | None:
    """Load the longest-history cached OHLCV file for a ticker."""
    clean = _norm_ticker(ticker).replace("^", "_").replace(" ", "_")
    matches = glob.glob(os.path.join(_CACHE_DIR, f"{clean}_*_1d_adjTrue.csv"))
    if not matches:
        return None
    best = None
    best_len = 0
    for path in matches:
        try:
            df = pd.read_csv(path, skiprows=[1, 2])
            df = df.rename(columns={"Price": "Date"})
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"]).set_index("Date").sort_index()
            for col in ("Open", "High", "Low", "Close", "Volume"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=["Close"])
            if len(df) > best_len:
                best_len = len(df)
                best = df
        except Exception:
            continue
    return best


def daily_return_map(ticker: str) -> dict[datetime, float]:
    df = load_cached(ticker)
    if df is None or df.empty:
        raise RuntimeError(f"No cached OHLCV for {ticker}")
    return {d.date(): float(r) for d, r in df["Close"].items()}


def daily_vix_map() -> dict[datetime, float]:
    return daily_return_map("^VIX")


def _tbill_factor(days: int) -> float:
    return (1.0 + _T_BILL_ANN) ** (days / 365.25) - 1.0


def interval_overlay_return(
    start_dt: datetime,
    end_dt: datetime,
    mode: str,
    prices: dict[datetime, float],
    vix: dict[datetime, float] | None,
    vix_threshold: float,
) -> float:
    """Return of the overlay vehicle over [start, end] as a decimal.

    mode:
      'tbill'  -> constant T-bill return
      'spy'    -> SPY total return
      'vix_spy' -> SPY when prior-day VIX <= threshold, else T-bill
    """
    days = max((end_dt - start_dt).days, 1)
    if mode == "tbill":
        return _tbill_factor(days)

    if mode in ("spy", "vix_spy"):
        d = start_dt.date()
        end_d = end_dt.date()
        ret = 1.0
        prev_vix: float | None = None
        current_d = d
        trading_days = 0
        tbill_days = 0
        while current_d <= end_d:
            use_spy = True
            if mode == "vix_spy" and vix is not None:
                # First day defaults to SPY; thereafter use prior-day VIX.
                if prev_vix is not None and prev_vix > vix_threshold:
                    use_spy = False

            if use_spy:
                p_today = prices.get(current_d)
                next_d = current_d + timedelta(days=1)
                while next_d <= end_d and next_d not in prices:
                    next_d += timedelta(days=1)
                if p_today is not None and next_d in prices:
                    ret *= prices[next_d] / p_today
                    trading_days += 1
            else:
                # Park in T-bills on high-VIX days.
                tbill_days += 1

            prev_vix = vix.get(current_d) if vix is not None else None
            current_d += timedelta(days=1)

        if trading_days == 0:
            return _tbill_factor(days)
        # Blend SPY return with pro-rated T-bill return for any T-bill days.
        if tbill_days:
            ret *= 1.0 + _tbill_factor(tbill_days)
        return ret - 1.0

    raise ValueError(f"Unknown overlay mode: {mode}")


def simulate(
    trades_df: pd.DataFrame,
    max_slots: int = 5,
    hold_td: int = 3,
    overlay_mode: str = "tbill",
    vix_threshold: float = 22.0,
    initial_capital: float = 10_000.0,
) -> dict:
    """Concurrent-position simulation with configurable idle-cash overlay."""
    df = trades_df.copy().sort_values("date").reset_index(drop=True)
    df["_entry_dt"] = pd.to_datetime(df["date"])
    # Calendar exit date from trading-day hold count (×1.4 approx)
    df["_exit_dt"] = df["_entry_dt"] + pd.to_timedelta((df["exit_day"].clip(lower=0) * 1.4 + 1).astype(int), unit="D")

    slot_size = 1.0 / max_slots
    capital = initial_capital
    peak = capital
    max_dd = 0.0
    open_slots: list = []  # [(exit_dt, net_pct, size_mult)]
    equity_log: list = [(df["_entry_dt"].iloc[0], capital)]
    skipped = 0
    last_event_dt = df["_entry_dt"].iloc[0]
    invested_time_accum = 0.0
    last_time = last_event_dt

    spy_prices = daily_return_map("SPY")
    vix_values = daily_vix_map()

    def _apply_idle(until_dt: datetime) -> None:
        nonlocal capital, last_event_dt, invested_time_accum, last_time
        if until_dt <= last_event_dt:
            return
        dt_days = (until_dt - last_event_dt).days
        invested_frac = len(open_slots) / max_slots
        invested_time_accum += invested_frac * dt_days
        last_time = until_dt

        idle_slots = max_slots - len(open_slots)
        if idle_slots <= 0:
            last_event_dt = until_dt
            return
        idle_frac = idle_slots / max_slots
        idle_ret = interval_overlay_return(
            last_event_dt,
            until_dt,
            overlay_mode,
            spy_prices,
            vix_values,
            vix_threshold,
        )
        capital *= 1.0 + idle_ret * idle_frac
        last_event_dt = until_dt

    for _, row in df.iterrows():
        entry_dt = row["_entry_dt"]
        exit_dt = row["_exit_dt"]
        net_pct = float(row["net_pct"])

        _apply_idle(entry_dt)

        # Close expired slots
        still_open = []
        for slot_exit, slot_pct, slot_mult in sorted(open_slots, key=lambda x: x[0]):
            if slot_exit <= entry_dt:
                _apply_idle(slot_exit)
                capital += capital * slot_size * slot_mult * (slot_pct / 100)
                peak = max(peak, capital)
                max_dd = max(max_dd, (peak - capital) / peak * 100)
                equity_log.append((slot_exit, round(capital, 4)))
            else:
                still_open.append((slot_exit, slot_pct, slot_mult))
        open_slots = still_open

        if len(open_slots) < max_slots:
            _mult = float(row.get("size_mult", 1.0)) if pd.notna(row.get("size_mult")) else 1.0
            open_slots.append((exit_dt, net_pct, _mult))
        else:
            skipped += 1

    # Drain remaining slots
    for slot_exit, slot_pct, slot_mult in sorted(open_slots, key=lambda x: x[0]):
        _apply_idle(slot_exit)
        capital += capital * slot_size * slot_mult * (slot_pct / 100)
        peak = max(peak, capital)
        max_dd = max(max_dd, (peak - capital) / peak * 100)
        equity_log.append((slot_exit, round(capital, 4)))

    if len(equity_log) < 10:
        return {}

    # Finalize time-weighted average invested fraction
    total_days = max((last_time - df["_entry_dt"].iloc[0]).days, 1)
    avg_invested_frac = invested_time_accum / total_days

    # Event-based Sharpe (consistent with run_portfolio_simulation)
    event_rets = []
    event_days_td = []
    for i in range(1, len(equity_log)):
        prev_dt, prev_cap = equity_log[i - 1]
        curr_dt, curr_cap = equity_log[i]
        if prev_cap > 0:
            cal_days = max((curr_dt - prev_dt).days, 1)
            event_rets.append((curr_cap / prev_cap - 1) * 100)
            event_days_td.append(max(cal_days * 252 / 365.25, 1.0))

    daily_equiv = [r / d for r, d in zip(event_rets, event_days_td)]
    mu_d = float(np.mean(daily_equiv))
    std_d = float(np.std(daily_equiv, ddof=1))
    sharpe_d = (mu_d - (_T_BILL_ANN / 252) * 100) / std_d if std_d > 0 else 0.0

    start_dt = equity_log[0][0]
    end_dt = equity_log[-1][0]
    years = max((end_dt - start_dt).days / 365.25, 1.0)
    cagr = (capital / initial_capital) ** (1.0 / years) - 1.0

    return {
        "overlay_mode": overlay_mode,
        "n_trades": len(df),
        "skipped": skipped,
        "final_capital": round(capital, 2),
        "cagr_pct": round(cagr * 100, 2),
        "max_dd_pct": round(max_dd, 2),
        "sharpe": round(sharpe_d, 3),
        "avg_invested_frac": round(avg_invested_frac, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest MR engine with residual cash overlay")
    parser.add_argument("--trades", type=str, default="data/mr_trades.csv")
    parser.add_argument("--max-slots", type=int, default=5)
    parser.add_argument("--hold-days", type=int, default=3)
    parser.add_argument("--vix-threshold", type=float, default=22.0)
    args = parser.parse_args()

    trades = pd.read_csv(args.trades)
    if "exit_day" not in trades.columns:
        trades["exit_day"] = args.hold_days

    print(f"Loaded {len(trades)} trades, max_slots={args.max_slots}, hold_days={args.hold_days}")

    results = []
    for mode in ("tbill", "spy", "vix_spy"):
        summary = simulate(
            trades,
            max_slots=args.max_slots,
            hold_td=args.hold_days,
            overlay_mode=mode,
            vix_threshold=args.vix_threshold,
        )
        results.append(summary)

    df = pd.DataFrame(results)
    print("\n=== Overlay Backtest Results ===")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
