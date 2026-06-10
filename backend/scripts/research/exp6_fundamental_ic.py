"""EXP6 — orthogonal FUNDAMENTAL signal screen (EDGAR, free, already on disk).

Price-factor IC is exhausted (EXP4). The orthogonal axis is non-price data. The
EDGAR pickle (data/edgar_fundamentals.pkl, from backtest_edgar.py) already holds
per-ticker POINT-IN-TIME series (indexed by SEC filing date → no lookahead) of:
  • piotroski  — 9-point F-score (accounting quality)
  • altman     — Z-score (distress; removed as a live *threshold* gate §76, but a
                 cross-sectional RANK may still carry info — tested here)
  • insider    — insider-buy clustering (smart-money)

We forward-fill each to a daily panel, z-score cross-sectionally, and measure:
  (1) rank IC vs forward returns at 5/10/21/42-day horizons (fundamentals are
      slow — the signal should live at the monthly+ horizon, matching the h=21
      cross-sectional model, NOT at 5d);
  (2) orthogonality vs the 8 price RAW_FEATURE_COLS (is it genuinely new info?).

Run in the prod venv (pure pandas/numpy; no alphalens needed):
    cd backend && source venv/bin/activate && python scripts/research/exp6_fundamental_ic.py
"""

from __future__ import annotations

import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from loader import CACHE, _latest_files, load_close

warnings.filterwarnings("ignore")

_EDGAR = Path(CACHE).parent / "edgar_fundamentals.pkl"


def _rowwise_spearman_ic(factor: pd.DataFrame, fwd: pd.DataFrame) -> pd.Series:
    rF, rR = factor.rank(axis=1), fwd.rank(axis=1)
    mask = rF.notna() & rR.notna()
    rF, rR = rF.where(mask), rR.where(mask)
    n = mask.sum(axis=1)
    dF, dR = rF.sub(rF.mean(axis=1), axis=0), rR.sub(rR.mean(axis=1), axis=0)
    ic = (dF * dR).sum(axis=1) / np.sqrt((dF**2).sum(axis=1) * (dR**2).sum(axis=1))
    return ic.where(n >= 8)


def _ic_stats(factor, close, horizons=(5, 10, 21, 42)):
    out = {}
    for hh in horizons:
        fwd = close.shift(-hh) / close - 1.0
        ic = _rowwise_spearman_ic(factor, fwd).dropna()
        if len(ic) < 50:
            out[hh] = (np.nan, np.nan, np.nan)
            continue
        m, sd = ic.mean(), ic.std()
        ir = m / sd if sd else np.nan
        out[hh] = (m, ir, ir * np.sqrt(len(ic)))
    return out


def _daily_panel(series_by_ticker: dict[str, pd.Series], date_index) -> pd.DataFrame:
    """Forward-fill each ticker's PIT (filing-date) series onto the daily index."""
    cols = {}
    for t, s in series_by_ticker.items():
        s = s[~s.index.duplicated(keep="last")].sort_index()
        cols[t] = s.reindex(date_index.union(s.index)).ffill().reindex(date_index)
    return pd.DataFrame(cols)


# ── load EDGAR + prices ────────────────────────────────────────────────────────
edgar = pickle.load(open(_EDGAR, "rb"))
tickers = list(edgar.keys())
files = _latest_files()
closes = {t: load_close(t, files[t]) for t in tickers if t in files}
closes = {t: s for t, s in closes.items() if s is not None}
close = pd.concat(closes, axis=1).sort_index()
close = close[close.index >= "2010-01-01"]
idx = close.index
print(f"EDGAR tickers: {len(tickers)} | with price history: {close.shape[1]} | days: {len(idx)}")


# ── build fundamental factor panels (PIT-aligned, ffilled) ─────────────────────
def _sub(name):
    return {
        t: edgar[t][name] for t in close.columns if isinstance(edgar[t].get(name), pd.Series) and len(edgar[t][name])
    }


piotroski = _daily_panel(_sub("piotroski"), idx)
altman = _daily_panel(_sub("altman"), idx)
insider = _daily_panel(_sub("insider"), idx)

factors = {
    "piotroski": piotroski,
    "piotroski_chg4q": piotroski - piotroski.shift(63),  # ~1y F-score improvement (quality momentum)
    "altman": altman,
    "altman_chg4q": altman - altman.shift(63),
    "insider": insider,
}

# ── IC screen ──────────────────────────────────────────────────────────────────
print(f"\n{'factor':<18}{'IC_5d':>9}{'IC_10d':>9}{'IC_21d':>9}{'IC_42d':>9}{'IR_21d':>9}{'t_21d':>9}  coverage")
print("-" * 92)
ic_rows = {}
for name, f in factors.items():
    cov = f.notna().mean().mean()
    st = _ic_stats(f, close)
    ic_rows[name] = st
    print(
        f"{name:<18}{st[5][0]:>9.4f}{st[10][0]:>9.4f}{st[21][0]:>9.4f}{st[42][0]:>9.4f}"
        f"{st[21][1]:>9.3f}{st[21][2]:>9.1f}  {cov:>5.0%}"
    )

# ── orthogonality vs the 8 price features (at the levels, cross-sectional z) ────
ret1 = close.pct_change()
gain = close.diff().clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
loss = (-close.diff().clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
price_feats = {
    "mom_12_1": close.shift(21) / close.shift(252) - 1,
    "rev_5": close / close.shift(5) - 1,
    "rev_21": close / close.shift(21) - 1,
    "vol_21": ret1.rolling(21).std(),
    "dist_ma50": close / close.rolling(50).mean() - 1,
    "rsi_14": 100 - 100 / (1 + gain / loss.replace(0, np.nan)),
}


def xs_z(df):
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0).clip(-3, 3)


allcols = {**{k: xs_z(v) for k, v in factors.items()}, **{k: xs_z(v) for k, v in price_feats.items()}}
stacked = pd.DataFrame({k: v.stack() for k, v in allcols.items()}).dropna()
corr = stacked.corr(method="spearman")

print("\nORTHOGONALITY — max |corr| of each fundamental factor vs the 6 price features:")
pf = list(price_feats.keys())
for name in factors:
    sub = corr.loc[name, pf].abs()
    verdict = "ORTHOGONAL ✅" if sub.max() < 0.30 else ("overlaps ⚠" if sub.max() < 0.6 else "REDUNDANT ✗")
    print(f"  {name:<18} max|corr|={sub.max():.2f} (vs {sub.idxmax()})   → {verdict}")

print("\nRead: fundamentals are slow — judge IC at 21d/42d. |IC|>0.02 with |t|>3 AND")
print("orthogonal (max|corr|<0.3) = a genuinely additive cross-sectional signal.")
