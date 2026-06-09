"""EXP2 — arch GARCH(1,1) vs trailing-realized vol, for sizing & barriers.

Two honest tests:
 (A) FORECAST: does GARCH(1,1) predict forward 10-day realized vol better than
     the trailing 21-day realized vol the engine effectively uses (ATR proxy)?
     Metric: Spearman corr & RMSE of forecast vs actual forward vol, pooled.
 (B) VOL-TARGETING: scale a long position to a 15% vol target using each
     estimator; better estimator => realized vol hugs target tighter (lower
     vol-of-vol) and ideally higher Sharpe. This is the sizing-layer payoff.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from arch import arch_model
from loader import close_panel, traded_tickers
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

panel = close_panel(traded_tickers()).dropna(axis=1, thresh=int(0.9 * 5139)).ffill().dropna()
rets = np.log(panel / panel.shift(1)).dropna()
H = 10  # forecast horizon (matches HOLD_DAYS=10)
TRAIN = 750  # ~3y rolling fit
STEP = 21  # refit monthly (GARCH refit is costly)
ANN = np.sqrt(252)

# ---------- (A) forecast accuracy, pooled across a liquid subset ----------
subset = list(rets.columns[:25])
g_fc, r_fc, actual = [], [], []
for tkr in subset:
    s = (rets[tkr] * 100).dropna()
    if len(s) < TRAIN + H + STEP:
        continue
    for i in range(TRAIN, len(s) - H, STEP):
        hist = s.iloc[:i]
        fwd = s.iloc[i : i + H]
        actual_vol = fwd.std()
        # trailing realized (what ATR/rolling-std approximates)
        realized = hist.iloc[-21:].std()
        # GARCH(1,1) forecast: mean of next-H daily vols
        try:
            res = arch_model(hist, vol="GARCH", p=1, q=1, dist="t", rescale=False).fit(disp="off")
            fc = res.forecast(horizon=H, reindex=False)
            garch_vol = np.sqrt(fc.variance.values[-1].mean())
        except Exception:
            continue
        if np.isfinite(garch_vol) and np.isfinite(realized) and np.isfinite(actual_vol):
            g_fc.append(garch_vol)
            r_fc.append(realized)
            actual.append(actual_vol)

g_fc, r_fc, actual = map(np.array, (g_fc, r_fc, actual))
g_rho = spearmanr(g_fc, actual).correlation
r_rho = spearmanr(r_fc, actual).correlation
g_rmse = np.sqrt(np.mean((g_fc - actual) ** 2))
r_rmse = np.sqrt(np.mean((r_fc - actual) ** 2))
print(f"(A) FORECAST of forward {H}d vol  (N={len(actual)} obs across {len(subset)} tickers)")
print(f"    {'estimator':<22}{'Spearman ρ':>12}{'RMSE':>10}")
print(f"    {'trailing realized 21d':<22}{r_rho:>12.3f}{r_rmse:>10.3f}")
print(f"    {'GARCH(1,1)-t':<22}{g_rho:>12.3f}{g_rmse:>10.3f}")
print(f"    => GARCH Δρ {g_rho - r_rho:+.3f}   ΔRMSE {g_rmse - r_rmse:+.3f} (negative=better)")

# ---------- (B) vol-targeting Sharpe & risk control on a market proxy ----------
proxy = "AAPL" if "AAPL" in rets.columns else rets.columns[0]
s = (rets[proxy] * 100).dropna()
TARGET = 1.0  # 1% daily ~ 16% annual
out = {"realized": [], "garch": [], "unscaled": []}
dates = []
for i in range(TRAIN, len(s) - 1, STEP):
    hist = s.iloc[:i]
    realized = hist.iloc[-21:].std()
    try:
        res = arch_model(hist, vol="GARCH", p=1, q=1, dist="t", rescale=False).fit(disp="off")
        garch_vol = np.sqrt(res.forecast(horizon=1, reindex=False).variance.values[-1][0])
    except Exception:
        garch_vol = realized
    nxt = s.iloc[i : i + STEP]  # realized fwd returns over the holding block
    w_real = TARGET / max(realized, 0.2)
    w_garch = TARGET / max(garch_vol, 0.2)
    out["realized"].append(nxt * w_real)
    out["garch"].append(nxt * w_garch)
    out["unscaled"].append(nxt)

print(f"\n(B) VOL-TARGETING on {proxy} (target {TARGET:.1f}%/day)")
print(f"    {'sizing':<22}{'AnnRet':>8}{'AnnVol':>8}{'Sharpe':>8}{'VolOfVol':>10}")
for k in ("unscaled", "realized", "garch"):
    r = pd.concat(out[k]) / 100.0
    ar = r.mean() * 252
    av = r.std() * ANN
    sh = ar / av if av else 0.0
    # realised vol stability: std of rolling-21d annualised vol around target
    vov = (r.rolling(21).std() * ANN).std()
    print(f"    {k:<22}{ar:>7.1%}{av:>8.1%}{sh:>8.2f}{vov:>10.3f}")
