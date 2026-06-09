"""EXP1b — HRP on dollar-neutral residual returns (the real proposed use case).

The long-only test understates HRP because one market factor dominates the
covariance. Strip it: residual_ret = ret - cross-sectional-mean each day (the
idiosyncratic leg of a dollar-neutral book). HRP's clustering should help most
on this heterogeneous, low-shared-beta structure.
"""

from __future__ import annotations

import warnings

import numpy as np
from loader import close_panel, traded_tickers
from skfolio import RiskMeasure
from skfolio.model_selection import WalkForward, cross_val_predict
from skfolio.optimization import EqualWeighted, HierarchicalRiskParity, InverseVolatility
from skfolio.preprocessing import prices_to_returns

warnings.filterwarnings("ignore")

panel = close_panel(traded_tickers()).dropna(axis=1, thresh=int(0.9 * 5139)).ffill().dropna()
X = prices_to_returns(panel)
# Strip the market factor → idiosyncratic residual returns (dollar-neutral leg).
Xn = X.sub(X.mean(axis=1), axis=0)
print(f"residual universe: {Xn.shape[1]} tickers, {Xn.shape[0]} days")

wf = WalkForward(train_size=252, test_size=21)
models = {
    "EqualWeight (baseline)": EqualWeighted(),
    "InverseVol": InverseVolatility(),
    "HRP-Variance": HierarchicalRiskParity(risk_measure=RiskMeasure.VARIANCE),
    "HRP-CVaR": HierarchicalRiskParity(risk_measure=RiskMeasure.CVAR),
}
ANN = 252
print(f"\n{'model':<24}{'AnnRet':>8}{'AnnVol':>8}{'Sharpe':>8}{'MaxDD':>9}")
print("-" * 55)
rows = {}
for name, model in models.items():
    pred = cross_val_predict(model, Xn, cv=wf, n_jobs=-1)
    r = np.asarray(pred.returns)
    ar, av = r.mean() * ANN, r.std() * np.sqrt(ANN)
    sh = ar / av if av else 0.0
    eq = np.cumprod(1 + r)
    dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    rows[name] = (ar, av, sh, dd)
    print(f"{name:<24}{ar:>7.1%}{av:>8.1%}{sh:>8.2f}{dd:>9.1%}")

b = rows["EqualWeight (baseline)"]
print("\nΔ vs EqualWeight (idiosyncratic risk-weighting):")
for name, (ar, av, sh, dd) in rows.items():
    if name.startswith("EqualWeight"):
        continue
    print(f"  {name:<22} ΔSharpe {sh - b[2]:+.2f}   ΔAnnVol {av - b[1]:+.1%}   ΔMaxDD {dd - b[3]:+.1%}")
