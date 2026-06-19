#!/usr/bin/env python3
"""Build the 2-year Massive IV panel and run the VRP / tail-capped straddle backtest,
isolating the Aug-2024 vol-spike week — the first real out-of-sample short-vol tail test.

Standalone: reads local Massive flat files, writes a parquet, runs the analysis directly
(does NOT touch the orats_daily_features DB table)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("massive_spike_backtest")

from scripts.orats_opportunity_model import (  # noqa: E402
    _VOL_FEATURES,
    _straddle_backtest,
    apply_universe_filter,
    engineer_features,
)
from services.massive_options_data import build_massive_panel  # noqa: E402

CACHE = _ROOT / "data" / "cache_massive"
PANEL = CACHE / "massive_panel_2y.parquet"
HORIZON = 2


def _universe() -> set[str]:
    u: set[str] = set()
    try:
        from scripts.backtest_technicals import TICKERS

        u |= set(TICKERS)
    except Exception:
        pass
    from scripts.orats_recommendation_engine import _INDEX_ETFS

    u |= _INDEX_ETFS
    u |= {"DBC", "DBA", "EEM", "VWO", "EWZ", "TLT", "BOTZ", "FAS"}  # liquid ETF VRP names
    return u


def main() -> None:
    if PANEL.exists():
        log.info("loading cached panel %s", PANEL)
        panel = pd.read_parquet(PANEL)
    else:
        log.info("building 2y panel (BS inversion over ~500 days — slow)…")
        panel = build_massive_panel(CACHE / "options", CACHE / "stocks", PANEL, universe=_universe())
    panel["date"] = pd.to_datetime(panel["date"])
    log.info(
        "panel: %d rows, %d dates (%s → %s), %d tickers",
        len(panel),
        panel["date"].nunique(),
        panel["date"].min().date(),
        panel["date"].max().date(),
        panel["ticker"].nunique(),
    )

    # Companies ≥$10B universe (same filter the live analysis uses).
    from scripts.orats_opportunity_model import _UNIVERSES

    at, cap, lbl = _UNIVERSES["companies"]
    filt = apply_universe_filter(panel, at, cap, lbl)
    feat = engineer_features(filt, HORIZON)
    feat["abs_move"] = feat["fwd_ret"].abs()
    feat.loc[feat["abs_move"] > 0.60, "abs_move"] = np.nan
    feat["impl_move"] = feat["atm_iv_30d"] * np.sqrt(HORIZON / 252.0)

    # Build the rich (sell-premium) cohort per day, walk-forward-style on the full panel.
    from scripts.orats_opportunity_model import _fill_per_date_median, _fit_predict

    d = feat[(feat["atm_iv_30d"] > 0.03) & (feat["atm_iv_30d"] < 4.0) & (feat["stk_px"] > 5)].copy()
    iv_rvol = d["atm_iv_30d"] / d["rvol20"].clip(lower=0.03)
    d = d[~(d["rvol20"].notna() & (iv_rvol > 8.0))]
    d = _fill_per_date_median(d, _VOL_FEATURES)
    lab = d.dropna(subset=["abs_move"])

    dates = np.array(sorted(d["date"].unique()))
    rows, last = [], None
    for i, dt in enumerate(dates[40:]):
        tr = lab[lab["date"] < dt]
        trd = np.array(sorted(tr["date"].unique()))
        if len(trd) <= HORIZON:
            continue
        tr = tr[tr["date"].isin(set(trd[: len(trd) - HORIZON]))]
        te = lab[lab["date"] == dt]
        if len(tr) < 1500 or te.empty:
            continue
        if last is None or i % 5 == 0:
            pred, last = _fit_predict("xgb", tr[_VOL_FEATURES].values, tr["abs_move"].values, te[_VOL_FEATURES].values)
        else:
            pred = last.predict(te[_VOL_FEATURES].values)
        o = te[["ticker", "date", "abs_move", "impl_move", "atm_iv_30d"]].copy()
        o["forecast_move"] = np.clip(pred, 1e-4, None)
        rows.append(o)
    val = pd.concat(rows, ignore_index=True)
    val["richness"] = val["impl_move"] / val["forecast_move"]
    val["rich_dec"] = val.groupby("date")["richness"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 10, labels=False)
    )
    rich = val[val["rich_dec"] == 9].copy()

    full = _straddle_backtest(rich, HORIZON)
    print("\n" + "=" * 70)
    print(f"  MASSIVE 2-YEAR VRP STRADDLE BACKTEST (companies, h={HORIZON}d)")
    print(f"  {val['date'].nunique()} test days, {val['date'].min().date()} → {val['date'].max().date()}")
    print("=" * 70)
    print(
        f"  FULL 2y rich cohort: net {full['mean_net'] * 100:+.2f}%/trade  win {full['win_rate'] * 100:.0f}%  "
        f"Sharpe {full['sharpe_ann']:+.1f}  worst {full['worst'] * 100:+.1f}%  hit-cap {full['pct_hit_cap'] * 100:.0f}%"
    )

    # Isolate the Aug-2024 spike week and a calm month for contrast.
    for label, lo, hi in [
        ("AUG-2024 SPIKE (07-29→08-16)", "2024-07-29", "2024-08-16"),
        ("calm month (2025-05)", "2025-05-01", "2025-05-31"),
    ]:
        sub = rich[(rich["date"] >= lo) & (rich["date"] <= hi)]
        if len(sub) < 5:
            print(f"  {label}: <5 trades")
            continue
        bt = _straddle_backtest(sub, HORIZON)
        print(
            f"  {label}: N={bt['n']} net {bt['mean_net'] * 100:+.2f}%/trade  win {bt['win_rate'] * 100:.0f}%  "
            f"worst {bt['worst'] * 100:+.1f}%  hit-cap {bt['pct_hit_cap'] * 100:.0f}%"
        )
    print("=" * 70)

    # Worst individual trades (where the tail lives).
    rich = rich.copy()
    rich["sell_pnl"] = rich["impl_move"] - rich["abs_move"]
    worst = rich.nsmallest(8, "sell_pnl")[["date", "ticker", "atm_iv_30d", "impl_move", "abs_move", "sell_pnl"]]
    worst = worst.assign(
        date=worst["date"].dt.date,
        iv=(worst["atm_iv_30d"] * 100).round(0),
        implied_pct=(worst["impl_move"] * 100).round(1),
        realized_pct=(worst["abs_move"] * 100).round(1),
        loss_pct=(worst["sell_pnl"] * 100).round(1),
    )
    print("\n  WORST 8 premium-sell trades (the tail):")
    print(worst[["date", "ticker", "iv", "implied_pct", "realized_pct", "loss_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
