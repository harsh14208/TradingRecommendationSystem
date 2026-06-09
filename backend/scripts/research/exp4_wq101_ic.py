"""EXP4 — WorldQuant-101 formulaic alphas: cross-sectional IC screen.

Question: is there untapped cross-sectional IC sitting in the free WorldQuant-101
factor library that the engine's IC-bound L/S model could use?

Pipeline:
  1. Build OHLCV panels from the engine's own cache_ohlcv/ (no new data).
  2. Implement the WQ-101 operator algebra + ~32 OHLCV-computable alphas.
  3. Score each alpha with alphalens methodology — daily cross-sectional rank IC
     vs forward returns at 1/5/10-day horizons, IR, t-stat, and turnover
     (factor rank autocorrelation).
  4. Cross-check the top factors against alphalens itself to confirm the fast
     vectorized IC matches.

Read: |mean IC| ~0.02-0.05 with |t|>3 and decent stability = a usable factor.
vwap is approximated by typical price (H+L+C)/3 (no intraday VWAP in the cache).
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from loader import ohlcv_panels

warnings.filterwarnings("ignore")

# ─────────────────────────── WQ-101 operator algebra ──────────────────────────
# Cross-sectional ops act per-date (axis=1); time-series ops act per-ticker
# (rolling over axis=0). Names follow Kakushadze (2016), "101 Formulaic Alphas".


def rank(df):  # cross-sectional percentile rank
    return df.rank(axis=1, pct=True)


def scale(df, a=1.0):  # rescale so sum|x| = a per date
    return df.mul(a).div(df.abs().sum(axis=1), axis=0)


def delay(df, d):
    return df.shift(d)


def delta(df, d):
    return df - df.shift(d)


def ts_sum(df, d):
    return df.rolling(d).sum()


def ts_mean(df, d):
    return df.rolling(d).mean()


def stddev(df, d):
    return df.rolling(d).std()


def ts_min(df, d):
    return df.rolling(d).min()


def ts_max(df, d):
    return df.rolling(d).max()


def product(df, d):
    return df.rolling(d).apply(np.prod, raw=True)


def ts_rank(df, d):
    return df.rolling(d).apply(lambda a: (a.argsort().argsort()[-1]) / (len(a) - 1), raw=True)


def ts_argmax(df, d):
    return df.rolling(d).apply(lambda a: float(np.argmax(a)), raw=True)


def ts_argmin(df, d):
    return df.rolling(d).apply(lambda a: float(np.argmin(a)), raw=True)


def decay_linear(df, d):
    w = np.arange(1, d + 1, dtype=float)
    w /= w.sum()
    return df.rolling(d).apply(lambda a: np.dot(a, w), raw=True)


def correlation(x, y, d):
    mx, my = x.rolling(d).mean(), y.rolling(d).mean()
    cov = (x * y).rolling(d).mean() - mx * my
    sx, sy = x.rolling(d).std(ddof=0), y.rolling(d).std(ddof=0)
    out = cov / (sx * sy)
    return out.replace([np.inf, -np.inf], np.nan)


def covariance(x, y, d):
    return (x * y).rolling(d).mean() - x.rolling(d).mean() * y.rolling(d).mean()


def signedpower(df, a):
    return np.sign(df) * df.abs().pow(a)


def sign(df):
    return np.sign(df)


# ─────────────────────────────── load + derive ────────────────────────────────
print("Loading OHLCV panels from cache_ohlcv/ …", flush=True)
P = ohlcv_panels()
o, h, low, c, v = P["open"], P["high"], P["low"], P["close"], P["volume"]
# common dense window
c = c.dropna(how="all")
idx = c.index
o, h, low, v = (df.reindex(idx) for df in (o, h, low, v))
returns = c.pct_change()
vwap = (h + low + c) / 3.0  # typical-price proxy (no intraday VWAP)
adv20 = (c * v).rolling(20).mean()
print(f"universe: {c.shape[1]} tickers × {c.shape[0]} days ({idx.min().date()}..{idx.max().date()})")


def _where(cond, a, b):
    return a.where(cond, b)


# ─────────────────────────────── alpha definitions ────────────────────────────
ALPHAS = {
    "a001": lambda: rank(ts_argmax(signedpower(_where(returns < 0, stddev(returns, 20), c), 2.0), 5)) - 0.5,
    "a002": lambda: -1 * correlation(rank(delta(np.log(v), 2)), rank((c - o) / o), 6),
    "a003": lambda: -1 * correlation(rank(o), rank(v), 10),
    "a004": lambda: -1 * ts_rank(rank(low), 9),
    "a005": lambda: rank(o - ts_sum(vwap, 10) / 10) * (-1 * (rank(c - vwap)).abs()),
    "a006": lambda: -1 * correlation(o, v, 10),
    "a007": lambda: _where(adv20 < v, -1 * ts_rank((delta(c, 7)).abs(), 60) * sign(delta(c, 7)), -1.0 + 0 * c),
    "a008": lambda: -1 * rank((ts_sum(o, 5) * ts_sum(returns, 5)) - delay(ts_sum(o, 5) * ts_sum(returns, 5), 10)),
    "a012": lambda: sign(delta(v, 1)) * (-1 * delta(c, 1)),
    "a013": lambda: -1 * rank(covariance(rank(c), rank(v), 5)),
    "a014": lambda: (-1 * rank(delta(returns, 3))) * correlation(o, v, 10),
    "a015": lambda: -1 * ts_sum(rank(correlation(rank(h), rank(v), 3)), 3),
    "a016": lambda: -1 * rank(covariance(rank(h), rank(v), 5)),
    "a017": lambda: ((-1 * rank(ts_rank(c, 10))) * rank(delta(delta(c, 1), 1))) * rank(ts_rank(v / adv20, 5)),
    "a018": lambda: -1 * rank(stddev((c - o).abs(), 5) + (c - o) + correlation(c, o, 10)),
    "a019": lambda: -1 * sign((c - delay(c, 7)) + delta(c, 7)) * (1 + rank(1 + ts_sum(returns, 250))),
    "a020": lambda: -1 * rank(o - delay(h, 1)) * rank(o - delay(c, 1)) * rank(o - delay(low, 1)),
    "a022": lambda: -1 * delta(correlation(h, v, 5), 5) * rank(stddev(c, 20)),
    "a025": lambda: rank((-1 * returns) * adv20 * vwap * (h - c)),
    "a026": lambda: -1 * ts_max(correlation(ts_rank(v, 5), ts_rank(h, 5), 5), 3),
    "a028": lambda: scale(correlation(adv20, low, 5) + (h + low) / 2 - c),
    "a033": lambda: rank(o / c - 1),
    "a034": lambda: rank((1 - rank(stddev(returns, 2) / stddev(returns, 5))) + (1 - rank(delta(c, 1)))),
    "a035": lambda: ts_rank(v, 32) * (1 - ts_rank(c + h - low, 16)) * (1 - ts_rank(returns, 32)),
    "a041": lambda: (h * low) ** 0.5 - vwap,
    "a043": lambda: ts_rank(v / adv20, 20) * ts_rank(-1 * delta(c, 7), 8),
    "a044": lambda: -1 * correlation(h, rank(v), 5),
    "a053": lambda: -1 * delta(((c - low) - (h - c)) / (c - low + 1e-12), 9),
    "a054": lambda: -1 * ((low - c) * (o**5)) / ((low - h + 1e-12) * (c**5)),
    "a101": lambda: (c - o) / ((h - low) + 1e-3),
}


# ─────────────────────────────── IC evaluation ────────────────────────────────
def _rowwise_pearson(A: pd.DataFrame, B: pd.DataFrame) -> pd.Series:
    """Per-row (per-date) Pearson corr between two aligned frames, NaN-aware."""
    mask = A.notna() & B.notna()
    A, B = A.where(mask), B.where(mask)
    n = mask.sum(axis=1)
    mA, mB = A.mean(axis=1), B.mean(axis=1)
    dA, dB = A.sub(mA, axis=0), B.sub(mB, axis=0)
    cov = (dA * dB).sum(axis=1)
    den = np.sqrt((dA**2).sum(axis=1) * (dB**2).sum(axis=1))
    out = cov / den
    return out.where(n >= 10)


def evaluate(factor: pd.DataFrame, horizons=(1, 5, 10)) -> dict:
    factor = factor.replace([np.inf, -np.inf], np.nan)
    rF = factor.rank(axis=1)
    res = {}
    for hh in horizons:
        fwd = c.shift(-hh) / c - 1.0
        ic = _rowwise_pearson(rF, fwd.rank(axis=1)).dropna()
        if len(ic) < 50:
            res[hh] = (np.nan, np.nan, np.nan)
            continue
        mean_ic, sd = ic.mean(), ic.std()
        ir = mean_ic / sd if sd else np.nan
        t = ir * np.sqrt(len(ic))
        res[hh] = (mean_ic, ir, t)
    # turnover proxy: day-to-day factor rank autocorrelation (higher = stabler)
    autocorr = _rowwise_pearson(rF, rF.shift(1)).dropna().mean()
    return {"ic": res, "autocorr": autocorr}


rows = []
for name, fn in ALPHAS.items():
    try:
        f = fn()
        if not isinstance(f, pd.DataFrame):
            continue
        r = evaluate(f)
        ic5, ir5, t5 = r["ic"][5]
        ic1 = r["ic"][1][0]
        ic10 = r["ic"][10][0]
        rows.append((name, ic1, ic5, ir5, t5, ic10, r["autocorr"]))
        print(f"  {name}  IC5={ic5:+.4f}  t5={t5:+.1f}", flush=True)
    except Exception as e:
        print(f"  {name}  FAILED: {e}", flush=True)

tab = pd.DataFrame(rows, columns=["alpha", "IC_1d", "IC_5d", "IR_5d", "t_5d", "IC_10d", "rank_autocorr"])
tab["abs_t5"] = tab["t_5d"].abs()
tab = tab.sort_values("abs_t5", ascending=False).drop(columns="abs_t5")

pd.set_option("display.float_format", lambda x: f"{x:+.4f}")
print("\n" + "=" * 78)
print("WORLDQUANT-101 CROSS-SECTIONAL IC SCREEN (ranked by |t| at 5-day horizon)")
print("=" * 78)
print(tab.to_string(index=False))

out_csv = "/tmp/wq101_ic_screen.csv"
tab.to_csv(out_csv, index=False)
print(f"\nsaved → {out_csv}")

# ── cross-check top-3 against alphalens (confirm vectorized IC matches) ─────────
try:
    from alphalens.performance import factor_information_coefficient
    from alphalens.utils import get_clean_factor_and_forward_returns

    print("\n── alphalens cross-check (top 3 by |t5|) ──")
    for name in tab["alpha"].head(3):
        f = ALPHAS[name]().replace([np.inf, -np.inf], np.nan)
        fac = f.stack()
        fac.index = fac.index.set_names(["date", "asset"])
        data = get_clean_factor_and_forward_returns(fac, c, quantiles=5, periods=(5,), max_loss=0.6)
        al_ic = factor_information_coefficient(data).iloc[:, 0].mean()
        mine = float(tab.loc[tab.alpha == name, "IC_5d"].iloc[0])
        print(f"  {name}: alphalens IC5={al_ic:+.4f}  vs  vectorized IC5={mine:+.4f}")
except Exception as e:
    print(f"alphalens cross-check skipped: {e}")
