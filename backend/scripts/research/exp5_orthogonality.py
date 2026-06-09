"""EXP5 — orthogonality of the 4 WQ-101 winners vs the model's existing features.

A new factor only helps an IC-bound model if it carries information the current
features don't. We replicate the 8 RAW_FEATURE_COLS from cross_sectional_alpha_
model.py and the 4 low-turnover WQ winners (a002/a004/a019/a026), cross-sectionally
z-score each per day (the model's exact normalization), and report the pooled
cross-sectional correlation matrix. |corr| < ~0.3 with every existing feature =
genuinely new information worth wiring in.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from loader import ohlcv_panels

warnings.filterwarnings("ignore")


# WQ operators (subset needed) ------------------------------------------------
def rank(df):
    return df.rank(axis=1, pct=True)


def delay(df, d):
    return df.shift(d)


def delta(df, d):
    return df - df.shift(d)


def ts_sum(df, d):
    return df.rolling(d).sum()


def ts_rank(df, d):
    return df.rolling(d).apply(lambda a: (a.argsort().argsort()[-1]) / (len(a) - 1), raw=True)


def ts_max(df, d):
    return df.rolling(d).max()


def correlation(x, y, d):
    mx, my = x.rolling(d).mean(), y.rolling(d).mean()
    cov = (x * y).rolling(d).mean() - mx * my
    sx, sy = x.rolling(d).std(ddof=0), y.rolling(d).std(ddof=0)
    return (cov / (sx * sy)).replace([np.inf, -np.inf], np.nan)


def sign(df):
    return np.sign(df)


P = ohlcv_panels()
o, h, low, c, v = P["open"], P["high"], P["low"], P["close"], P["volume"]
idx = c.dropna(how="all").index
o, h, low, v = (df.reindex(idx) for df in (o, h, low, v))
ret1 = c.pct_change()
print(f"universe: {c.shape[1]} tickers × {len(idx)} days")

# Existing model features (replicated from add_price_features) -----------------
feat = {}
feat["mom_12_1"] = c.shift(21) / c.shift(252) - 1.0
feat["rev_5"] = c / c.shift(5) - 1.0
feat["rev_21"] = c / c.shift(21) - 1.0
feat["vol_21"] = ret1.rolling(21).std()
feat["dollar_vol_21"] = (c * v).rolling(21).mean()
feat["dist_ma50"] = c / c.rolling(50).mean() - 1.0
gain = c.diff().clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
loss = (-c.diff().clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
feat["rsi_14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

# WQ-101 winners --------------------------------------------------------------
feat["wq002"] = -1 * correlation(rank(delta(np.log(v), 2)), rank((c - o) / o), 6)
feat["wq004"] = -1 * ts_rank(rank(low), 9)
feat["wq019"] = -1 * sign((c - delay(c, 7)) + delta(c, 7)) * (1 + rank(1 + ts_sum(ret1, 250)))
feat["wq026"] = -1 * ts_max(correlation(ts_rank(v, 5), ts_rank(h, 5), 5), 3)


def xs_z(df):
    """Same-day cross-sectional z-score, clipped ±3 (matches the model)."""
    z = df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)
    return z.clip(-3, 3)


cols = list(feat.keys())
stacked = {k: xs_z(feat[k]).stack() for k in cols}
M = pd.DataFrame(stacked).dropna()
corr = M.corr(method="spearman")

pd.set_option("display.float_format", lambda x: f"{x:+.2f}")
pd.set_option("display.width", 160)
print(f"\npooled cross-sectional correlation (N={len(M):,} ticker-days)\n")
print(corr.round(2).to_string())

existing = ["mom_12_1", "rev_5", "rev_21", "vol_21", "dollar_vol_21", "dist_ma50", "rsi_14"]
wq = ["wq002", "wq004", "wq019", "wq026"]
print("\nmax |corr| of each WQ alpha vs the 7 existing price features:")
for a in wq:
    sub = corr.loc[a, existing].abs()
    worst = sub.idxmax()
    verdict = "ORTHOGONAL ✅" if sub.max() < 0.30 else ("overlaps ⚠" if sub.max() < 0.6 else "REDUNDANT ✗")
    print(f"  {a}: max|corr|={sub.max():.2f} (vs {worst})   → {verdict}")
