"""Standalone 23-year backtest of the QENG alpha *sleeves* — starting with the
residual stat-arb sleeve (QENG-5a), which `alpha_sleeves.py` computes as a live
signal but which has NEVER been validated as a strategy (the cross-sleeve
allocator currently runs on placeholder Sharpes of 1.0 and a single AAPL/MSFT pair).

Residual stat-arb (Avellaneda-Lee style): regress 60d daily stock returns on the
sector-ETF returns, trade the residual's mean-reversion. Market-neutral — P&L is
the beta-hedged residual (long stock / short β×ETF), so it should be ~uncorrelated
with the long-only MR book. If it carries a real, low-correlation edge, combining
it with MR raises portfolio Sharpe beyond the single-strategy MR ceiling.

Usage:
    python scripts/backtest_sleeves.py            # IS universe
    python scripts/backtest_sleeves.py --oos      # held-out universe
"""

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")

from scripts.backtest_technicals import (  # noqa: E402
    END,
    START,
    TICKER_TO_SECTOR,
    TICKERS,
    cached_yf_download,
)

try:
    from scripts.backtest_technicals import HELD_OUT_TICKERS  # noqa: E402
except Exception:
    HELD_OUT_TICKERS = []

# ── Parameters ───────────────────────────────────────────────────────────────
# Corrected formulation: trade the cumulative PRICE-SPREAD residual (Engle-Granger /
# Avellaneda-Lee), which mean-reverts over days, NOT the daily-return residual the
# live sleeve uses (that churns at a 1-day half-life and dies on friction).
LOOKBACK = 60          # spread regression / z-score window (days)
Z_ENTRY = 2.0          # enter when |spread z| > 2
Z_EXIT = 0.5           # exit when spread reverts toward the mean
HALF_LIFE_MAX = 30.0   # OU half-life filter on the spread (days)
MAX_HOLD = 30          # safety time-exit (days) — spread reversion is multi-day
FRICTION_2LEG = 0.65   # round-trip friction, stock leg (~0.50%) + liquid ETF leg (~0.15%)


def _close_series(df):
    """Extract a float Close series from a (possibly MultiIndex) cached frame."""
    if df is None or len(df) == 0:
        return None
    cols = df.columns
    if isinstance(cols, pd.MultiIndex):
        lvl0 = cols.get_level_values(0)
        if "Close" in lvl0:
            s = df["Close"]
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            return pd.to_numeric(s, errors="coerce").dropna()
        return None
    if "Close" in cols:
        return pd.to_numeric(df["Close"], errors="coerce").dropna()
    return None


def _sector_etf(ticker: str) -> str | None:
    return TICKER_TO_SECTOR.get(ticker)


def compute_signals(ticker: str, etf: str, close_s: pd.Series, close_e: pd.Series):
    """Compute the per-day spread z-score, half-life, beta ONCE (the expensive part).
    Returns (dates, s, e, z[], half_life[], beta[]) or None. Indices align to prices;
    entries [0:LOOKBACK] are NaN/unused."""
    df = pd.DataFrame({"s": close_s, "e": close_e}).dropna()
    if len(df) < LOOKBACK + 30:
        return None
    s = df["s"].to_numpy(dtype=float)
    e = df["e"].to_numpy(dtype=float)
    if (s <= 0).any() or (e <= 0).any():
        return None
    ls, le = np.log(s), np.log(e)
    n = len(ls)
    z = np.full(n, np.nan)
    hl = np.full(n, 99.0)
    bt = np.full(n, np.nan)
    for i in range(LOOKBACK, n):
        ws = ls[i - LOOKBACK : i]
        we = le[i - LOOKBACK : i]
        A = np.column_stack([np.ones_like(we), we])
        coef, *_ = np.linalg.lstsq(A, ws, rcond=None)
        alpha, beta = float(coef[0]), float(coef[1])
        spread_win = ws - (alpha + beta * we)
        spread_now = ls[i] - (alpha + beta * le[i])
        mu, sd = float(spread_win.mean()), max(float(spread_win.std()), 1e-9)
        z[i] = (spread_now - mu) / sd
        xt, xtm1 = spread_win[1:], spread_win[:-1]
        A_ou = np.column_stack([np.ones_like(xtm1), xtm1])
        coef_ou, *_ = np.linalg.lstsq(A_ou, xt, rcond=None)
        a_param = float(coef_ou[1])
        hl[i] = (-np.log(2.0) / np.log(a_param)) if 0 < a_param < 1.0 else 99.0
        bt[i] = beta
    return df.index, s, e, z, hl, bt


def simulate_from_signals(sig, ticker, etf, z_entry, z_exit=Z_EXIT, max_hold=MAX_HOLD) -> list[dict]:
    """Cheap pass: simulate trades from precomputed signals at a given entry threshold."""
    dates, s, e, z, hl, bt = sig
    trades: list[dict] = []
    pos = None
    for i in range(LOOKBACK, len(z)):
        if np.isnan(z[i]):
            continue
        if pos is None:
            if abs(z[i]) > z_entry and hl[i] < HALF_LIFE_MAX:
                direction = 1 if z[i] < -z_entry else -1
                pos = {"entry_i": i, "direction": direction, "beta": float(bt[i]), "z_entry": float(z[i])}
        else:
            held = i - pos["entry_i"]
            reverted = (pos["direction"] == 1 and z[i] >= -z_exit) or (pos["direction"] == -1 and z[i] <= z_exit)
            if reverted or held >= max_hold:
                ei = pos["entry_i"]
                cum_s = s[i] / s[ei] - 1.0
                cum_e = e[i] / e[ei] - 1.0
                resid_ret = pos["direction"] * (cum_s - pos["beta"] * cum_e) * 100.0
                trades.append({
                    "date": dates[ei], "exit_date": dates[i], "ticker": ticker, "etf": etf,
                    "direction": pos["direction"], "held": held,
                    "z_entry": round(pos["z_entry"], 2), "net_pct": round(resid_ret - FRICTION_2LEG, 3),
                })
                pos = None
    return trades


# TS-momentum basket (UUP substituted for the non-tradeable DXY index).
TREND_BASKET = ["SPY", "QQQ", "TLT", "GLD", "UUP", "HYG"]
SMA_N = 200


def backtest_tsmom(closes: dict[str, pd.Series], long_short: bool) -> dict:
    """Time-series momentum sleeve over a macro-ETF basket.

    Signal = sign(price − SMA200) applied causally (yesterday's signal × today's
    return). long_short=False → long-flat (the live sleeve's rule); True → long-short
    (classic TSMOM / crisis-alpha). Equal-weight across available ETFs. Returns daily
    basket returns + annualised metrics; daily series is the crisis-alpha diversifier
    candidate to correlate against the MR book.
    """
    per_etf_daily = {}
    for etf, cs in closes.items():
        if cs is None or len(cs) < SMA_N + 50:
            continue
        px = cs.to_numpy(dtype=float)
        sma = pd.Series(px).rolling(SMA_N).mean().to_numpy()
        ret = np.zeros(len(px))
        ret[1:] = px[1:] / px[:-1] - 1.0
        sig = np.where(px > sma, 1.0, (-1.0 if long_short else 0.0))
        strat = np.zeros(len(px))
        strat[1:] = sig[:-1] * ret[1:]  # causal: yesterday's signal
        per_etf_daily[etf] = pd.Series(strat, index=cs.index)
    if not per_etf_daily:
        return {}
    basket = pd.DataFrame(per_etf_daily).dropna(how="all").mean(axis=1).dropna()
    basket = basket.iloc[SMA_N:]  # drop warmup
    a = basket.to_numpy()
    mu, sd = float(a.mean()), float(a.std(ddof=1))
    ann_sharpe = round((mu / sd) * np.sqrt(252), 3) if sd > 0 else None
    eq, peak, mdd = 1.0, 1.0, 0.0
    for r in a:
        eq *= 1 + r
        peak = max(peak, eq)
        mdd = max(mdd, (peak - eq) / peak * 100)
    yrs = len(a) / 252
    cagr = round((eq ** (1 / yrs) - 1) * 100, 2) if yrs > 0 and eq > 0 else None
    return {"ann_sharpe": ann_sharpe, "cagr": cagr, "max_dd": round(mdd, 2),
            "n_days": len(a), "etfs": list(per_etf_daily.keys()), "daily": basket}


def stats(rets: list[float]) -> dict:
    if not rets:
        return {"n": 0, "wr": 0.0, "avg": 0.0, "sharpe": None, "max_dd": 0.0}
    a = np.array(rets, dtype=float)
    n = len(a)
    mu, sd = float(a.mean()), float(a.std(ddof=1)) if n > 1 else 0.0
    sharpe = round(mu / sd, 4) if sd > 0 and n >= 10 else None
    cap, peak, mdd = 1.0, 1.0, 0.0
    for r in a:
        cap *= 1 + 0.05 * (r / 100)  # 5% position size, sequential
        peak = max(peak, cap)
        mdd = max(mdd, (peak - cap) / peak * 100)
    return {"n": n, "wr": round(float((a > 0).mean()) * 100, 1), "avg": round(mu, 2),
            "sharpe": sharpe, "max_dd": round(mdd, 2)}


def run_tsmom():
    print(f"## TS-Momentum Sleeve Backtest ({START} → {END})\n")
    print(f"> Signal = sign(price − SMA{SMA_N}), causal; equal-weight basket {TREND_BASKET}.\n")
    closes = {etf: _close_series(cached_yf_download(etf, START, END)) for etf in TREND_BASKET}

    # Buy-and-hold equal-weight basket baseline — isolates trend-timing alpha vs basket beta.
    bh_daily = {}
    for etf, cs in closes.items():
        if cs is not None and len(cs) > SMA_N + 50:
            px = cs.to_numpy(dtype=float)
            r = np.zeros(len(px)); r[1:] = px[1:] / px[:-1] - 1.0
            bh_daily[etf] = pd.Series(r, index=cs.index)
    if bh_daily:
        bh = pd.DataFrame(bh_daily).dropna(how="all").mean(axis=1).dropna().iloc[SMA_N:]
        a = bh.to_numpy()
        bh_sh = round((a.mean() / a.std()) * np.sqrt(252), 3) if a.std() > 0 else None
        eq, peak, mdd = 1.0, 1.0, 0.0
        for x in a:
            eq *= 1 + x; peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak * 100)
        print(f"> Buy-hold equal-weight basket baseline: Ann.Sharpe {bh_sh}, MaxDD -{mdd:.1f}% "
              f"(trend-timing must beat this to be real alpha).\n")

    print("| Variant | ETFs | Days | CAGR | Ann.Sharpe | MaxDD |")
    print("|:---|---:|---:|---:|---:|---:|")
    saved = None
    for ls, lbl in [(False, "Long-flat (sleeve rule)"), (True, "Long-short (classic TSMOM)")]:
        r = backtest_tsmom(closes, ls)
        if not r:
            print(f"| {lbl} | — | — | — | — | — |")
            continue
        print(f"| {lbl} | {len(r['etfs'])} | {r['n_days']} | "
              f"{r['cagr'] if r['cagr'] is not None else '—'}% | "
              f"{r['ann_sharpe'] if r['ann_sharpe'] else '—'} | -{r['max_dd']:.1f}% |")
        if saved is None or (r.get("ann_sharpe") or -9) > (saved.get("ann_sharpe") or -9):
            saved = r
    if saved and saved.get("daily") is not None:
        m = saved["daily"].resample("ME").apply(lambda x: (1 + x).prod() - 1)
        m.index = m.index.to_period("M").astype(str)  # match mr_monthly.csv key format
        m.to_csv("data/tsmom_monthly.csv")
        sh = saved.get("ann_sharpe") or 0
        print(f"\n> Best ann.Sharpe {sh}. " + (
            "✅ standalone trend edge — proceed to MR-correlation (diversification) test."
            if sh > 0.2 else "➖ weak standalone; correlation with MR may still make it a useful hedge."
            if sh > 0 else "⚠ no standalone trend edge on this basket."))
        print("> Monthly series → data/tsmom_monthly.csv (for MR-correlation step).\n")


def run_corr():
    """Quantify diversification: correlate each sleeve's monthly returns with the MR
    book and compute the combined-portfolio Sharpe vs MR-only. Requires data/mr_monthly.csv
    (from a backtest_technicals run) + data/tsmom_monthly.csv / data/statarb_monthly_is.csv."""
    import os
    print("## Sleeve × MR Diversification Test (monthly returns)\n")
    if not os.path.exists("data/mr_monthly.csv"):
        print("> Missing data/mr_monthly.csv — run `python scripts/backtest_technicals.py --sequential` first.\n")
        return
    mr = pd.read_csv("data/mr_monthly.csv", index_col=0).iloc[:, 0]
    mr.index = mr.index.astype(str)
    sleeves = {"TS-Momentum": "data/tsmom_monthly.csv", "Stat-Arb": "data/statarb_monthly_is.csv"}
    print("| Sleeve | Months | Corr w/ MR | MR Sharpe | Sleeve Sharpe | 50/50 Risk-Blend | Δ vs MR |")
    print("|:---|---:|---:|---:|---:|---:|---:|")
    for name, path in sleeves.items():
        if not os.path.exists(path):
            print(f"| {name} | — | (run sleeve first) | — | — | — |")
            continue
        sl = pd.read_csv(path, index_col=0).iloc[:, 0]
        sl.index = sl.index.astype(str)
        j = pd.DataFrame({"mr": mr, "sl": sl}).dropna()
        if len(j) < 12:
            print(f"| {name} | {len(j)} | too few | — | — | — |")
            continue
        corr = float(j["mr"].corr(j["sl"]))
        # Equal-RISK blend (vol-normalise each leg) so the diversification benefit isn't
        # masked by the two series having different return scales/units.
        mrn = j["mr"] / j["mr"].std()
        sln = j["sl"] / j["sl"].std()
        mr_sh = (mrn.mean() / mrn.std() * np.sqrt(12)) if mrn.std() > 0 else 0.0
        comb = 0.5 * mrn + 0.5 * sln
        cb_sh = (comb.mean() / comb.std() * np.sqrt(12)) if comb.std() > 0 else 0.0
        sl_sh = (sln.mean() / sln.std() * np.sqrt(12)) if sln.std() > 0 else 0.0
        print(f"| {name} | {len(j)} | {corr:+.2f} | {mr_sh:.2f} | {sl_sh:.2f} | {cb_sh:.2f} | {cb_sh - mr_sh:+.2f} |")
    print("\n> Equal-risk (vol-normalised) monthly Sharpes ×√12. Combined = 50/50 risk blend.")
    print("> Low corr + combined Sharpe > both legs ⇒ the sleeve genuinely diversifies the MR book.\n")


def main():
    if "--ts" in sys.argv:
        run_tsmom()
        return
    if "--corr" in sys.argv:
        run_corr()
        return
    oos = "--oos" in sys.argv
    universe = HELD_OUT_TICKERS if oos else TICKERS
    label = "OOS held-out" if oos else "IS"
    z_sweep = [2.0, 2.5, 3.0, 3.5]
    print(f"## Residual Stat-Arb Sleeve Backtest — {label} ({START} → {END})\n")
    print(f"> Spread-level (log-price cointegration), half-life<{HALF_LIFE_MAX}d; exit |z|<{Z_EXIT} or "
          f"{MAX_HOLD}d; friction {FRICTION_2LEG}% (2 legs). Sweeping entry |z|.\n")

    etfs = sorted({_sector_etf(t) for t in universe if _sector_etf(t)})
    etf_close = {etf: _close_series(cached_yf_download(etf, START, END)) for etf in etfs}

    # Compute per-ticker signals ONCE (the expensive OLS pass).
    sigs = []
    skipped = 0
    for t in universe:
        etf = _sector_etf(t)
        if not etf or etf_close.get(etf) is None:
            skipped += 1
            continue
        cs = _close_series(cached_yf_download(t, START, END))
        if cs is None:
            skipped += 1
            continue
        sig = compute_signals(t, etf, cs, etf_close[etf])
        if sig is not None:
            sigs.append((t, etf, sig))

    print(f"> Universe {len(universe)} tickers ({skipped} skipped), {len(sigs)} with signals.\n")
    print("| Entry |z| | N | WR | Avg Ret | Avg Hold | Per-Trade Sharpe | Ann.Sharpe | MaxDD |")
    print("|:---|---:|---:|---:|---:|---:|---:|---:|")
    best = None
    for ze in z_sweep:
        trades = []
        for t, etf, sig in sigs:
            trades.extend(simulate_from_signals(sig, t, etf, ze))
        if not trades:
            continue
        tdf = pd.DataFrame(trades)
        s = stats(tdf["net_pct"].tolist())
        avg_hold = tdf["held"].mean()
        periods_yr = 252 / max(avg_hold, 1)
        ann = round(s["sharpe"] * np.sqrt(periods_yr), 3) if s["sharpe"] else None
        print(f"| {ze:.1f} | {s['n']} | {s['wr']:.1f}% | {s['avg']:+.2f}% | {avg_hold:.1f}d | "
              f"{s['sharpe'] if s['sharpe'] is not None else '—'} | {ann if ann else '—'} | -{s['max_dd']:.1f}% |")
        if (s["sharpe"] or -9) > (best[1]["sharpe"] if best else -9):
            best = (ze, s, tdf, ann)

    if best is None:
        print("\n> No trades generated.")
        return
    ze, s, tdf, ann = best
    pos_edge = (s["sharpe"] or 0) > 0.02
    print(f"\n> Best entry |z|={ze}: per-trade Sharpe {s['sharpe']}, ann {ann}.")
    print("> Verdict: " + (
        f"✅ positive standalone edge at |z|≥{ze} — proceed to MR-correlation test"
        if pos_edge else
        "⚠ even at higher thresholds the sector-ETF residual edge stays below friction — "
        "sector-ETF stat-arb is not viable on this universe; next try true stock-stock cointegrated pairs "
        "or the TS-momentum sleeve."))
    # Save best-config monthly series for the MR-correlation step.
    tdf["_m"] = pd.to_datetime(tdf["exit_date"]).dt.to_period("M").astype(str)
    tdf.groupby("_m")["net_pct"].mean().to_csv(f"data/statarb_monthly_{'oos' if oos else 'is'}.csv")
    print(f"\n> Best-config monthly series → data/statarb_monthly_{'oos' if oos else 'is'}.csv\n")


if __name__ == "__main__":
    main()
