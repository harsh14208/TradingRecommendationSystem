"""EXP7 — academic fundamental factor-zoo IC + orthogonality screen.

Consumes data/fundamental_factors.pkl (scripts/build_fundamental_factors.py) and
forms the classic orthogonal-to-price factors cross-sectionally, oriented so a
POSITIVE IC = the factor works in its documented direction:
  • value_bm      = book equity / market cap            (value premium; high=cheap=good)
  • gross_prof    = gross profit / assets               (Novy-Marx; high=good)
  • accruals_neg  = −(net income − op cash flow)/assets (Sloan; low accruals=good)
  • asset_grw_neg = −ΔAssets YoY                         (investment factor; low=good)
  • issuance_neg  = −Δshares YoY                         (buyback=good)
  • piotroski_chg = ΔF-score ~1y                         (quality momentum; EXP6 winner)
Plus net_insider (data/net_insider.pkl) if the Form 4 scrape has finished.

Flow items use a trailing-4-filing sum (≈TTM) to smooth 10-Q/10-K scale mixing;
all series are PIT (filing-date) ffilled to daily. Judge IC at 21d/42d/63d.

    cd backend && source venv/bin/activate && python scripts/research/exp7_factor_zoo_ic.py
"""

from __future__ import annotations

import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from loader import CACHE, _latest_files, load_close

warnings.filterwarnings("ignore")
_DATA = Path(CACHE).parent


def _ic(factor, fwd):
    rF, rR = factor.rank(axis=1), fwd.rank(axis=1)
    m = rF.notna() & rR.notna()
    rF, rR = rF.where(m), rR.where(m)
    n = m.sum(axis=1)
    dF, dR = rF.sub(rF.mean(axis=1), axis=0), rR.sub(rR.mean(axis=1), axis=0)
    ic = (dF * dR).sum(axis=1) / np.sqrt((dF**2).sum(axis=1) * (dR**2).sum(axis=1))
    return ic.where(n >= 8)


def _ic_stats(factor, close, horizons=(5, 21, 42, 63)):
    out = {}
    for hh in horizons:
        ic = _ic(factor, close.shift(-hh) / close - 1.0).dropna()
        if len(ic) < 50:
            out[hh] = (np.nan, np.nan, np.nan)
        else:
            m, sd = ic.mean(), ic.std()
            ir = m / sd if sd else np.nan
            out[hh] = (m, ir, ir * np.sqrt(len(ic)))
    return out


def _daily(series_by_ticker, idx):
    cols = {}
    for t, s in series_by_ticker.items():
        if s is None or not len(s):
            continue
        s = s[~s.index.duplicated(keep="last")].sort_index()
        cols[t] = s.reindex(idx.union(s.index)).ffill().reindex(idx)
    return pd.DataFrame(cols)


def xs_z(df):
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0).clip(-3, 3)


# ── load ───────────────────────────────────────────────────────────────────────
fund = pickle.load(open(_DATA / "fundamental_factors.pkl", "rb"))
tickers = list(fund.keys())
files = _latest_files()
close = pd.concat({t: load_close(t, files[t]) for t in tickers if t in files}, axis=1).sort_index()
close = close[close.index >= "2010-01-01"]
idx = close.index
tickers = [t for t in tickers if t in close.columns]
print(f"tickers: {len(tickers)} | days: {len(idx)}")


def concept(name, ttm=False):
    """Daily ffilled panel of a stored concept; ttm=True → trailing-4-filing sum (flows)."""
    raw = {}
    for t in tickers:
        s = fund[t].get(name)
        if s is None or not len(s):
            continue
        s = s[~s.index.duplicated(keep="last")].sort_index()
        raw[t] = s.rolling(4, min_periods=2).sum() if ttm else s
    return _daily(raw, idx)


book = concept("book_equity")
assets = concept("assets")
shares = concept("shares_out")
ni_ttm = concept("net_income", ttm=True)
ocf_ttm = concept("op_cash_flow", ttm=True)
rev_ttm = concept("revenue", ttm=True)
gp_ttm = concept("gross_profit", ttm=True)
cor_ttm = concept("cost_of_revenue", ttm=True)
gp_ttm = gp_ttm.where(gp_ttm.notna(), rev_ttm - cor_ttm)  # derive GP where not reported

mktcap = shares * close
# YoY on quarterly series → ~252 trading days after ffill
factors = {
    "value_bm": book / mktcap,
    "gross_prof": gp_ttm / assets,
    "accruals_neg": -(ni_ttm - ocf_ttm) / assets,
    "asset_grw_neg": -(assets / assets.shift(252) - 1),
    "issuance_neg": -(shares / shares.shift(252) - 1),
}
# piotroski change from the original pickle
pio = _daily({t: fund[t].get("piotroski") for t in tickers}, idx)
factors["piotroski_chg"] = pio - pio.shift(63)

# net insider (optional — only if the Form 4 scrape finished)
ni_path = _DATA / "net_insider.pkl"
if ni_path.exists():
    netins = pickle.load(open(ni_path, "rb"))
    ni_panel = _daily(netins, idx)
    if ni_panel.shape[1] >= 10:
        factors["net_insider_buy"] = ni_panel / shares.reindex_like(ni_panel)  # normalize by shares out

# ── IC screen ──────────────────────────────────────────────────────────────────
print(f"\n{'factor':<16}{'IC_5d':>9}{'IC_21d':>9}{'IC_42d':>9}{'IC_63d':>9}{'IR_42d':>9}{'t_42d':>9}  cov")
print("-" * 86)
for name, f in factors.items():
    f = f.replace([np.inf, -np.inf], np.nan)
    st = _ic_stats(f, close)
    print(
        f"{name:<16}{st[5][0]:>9.4f}{st[21][0]:>9.4f}{st[42][0]:>9.4f}{st[63][0]:>9.4f}"
        f"{st[42][1]:>9.3f}{st[42][2]:>9.1f}  {f.notna().mean().mean():>4.0%}"
    )

# ── orthogonality vs price + among fundamentals ────────────────────────────────
ret1 = close.pct_change()
gain = close.diff().clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
loss = (-close.diff().clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
price_feats = {
    "mom_12_1": close.shift(21) / close.shift(252) - 1,
    "rev_21": close / close.shift(21) - 1,
    "vol_21": ret1.rolling(21).std(),
    "dist_ma50": close / close.rolling(50).mean() - 1,
    "rsi_14": 100 - 100 / (1 + gain / loss.replace(0, np.nan)),
}
allz = {
    **{k: xs_z(v.replace([np.inf, -np.inf], np.nan)) for k, v in factors.items()},
    **{k: xs_z(v) for k, v in price_feats.items()},
}
corr = pd.DataFrame({k: v.stack() for k, v in allz.items()}).dropna().corr(method="spearman")
pf = list(price_feats.keys())
print("\nORTHOGONALITY — max |corr| vs price features:")
for name in factors:
    sub = corr.loc[name, pf].abs()
    v = "ORTHOGONAL ✅" if sub.max() < 0.30 else ("overlaps ⚠" if sub.max() < 0.6 else "REDUNDANT ✗")
    print(f"  {name:<16} max|corr|={sub.max():.2f} (vs {sub.idxmax()})  → {v}")
print("\nRead: judge fundamentals at 42d/63d; |IC|>0.02, |t|>3, orthogonal = add it.")
