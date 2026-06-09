"""EXP1 — skfolio portfolio construction vs equal-weight, walk-forward OOS.

Question: holding the engine's tradeable universe, does Hierarchical Risk Parity
(or inverse-vol / min-variance) reduce drawdown vs equal-weight at similar return?
This is the concurrent-book construction layer (current: sector caps + half-Kelly
+ vol-scale + §83 corr cut, deciles equal-weighted).

Walk-forward: fit on trailing 252d, hold 21d OOS, roll. Pure out-of-sample.
"""

from __future__ import annotations

import warnings

import numpy as np
from loader import close_panel, traded_tickers
from skfolio import RiskMeasure
from skfolio.model_selection import WalkForward, cross_val_predict
from skfolio.optimization import (
    EqualWeighted,
    HierarchicalRiskParity,
    InverseVolatility,
    MeanRisk,
    ObjectiveFunction,
)
from skfolio.preprocessing import prices_to_returns

warnings.filterwarnings("ignore")

panel = close_panel(traded_tickers()).dropna(axis=1, thresh=int(0.9 * 5139))
panel = panel.ffill().dropna()
print(
    f"universe: {panel.shape[1]} tickers, {panel.shape[0]} days "
    f"({panel.index.min().date()}..{panel.index.max().date()})"
)

X = prices_to_returns(panel)
wf = WalkForward(train_size=252, test_size=21)

models = {
    "EqualWeight (baseline)": EqualWeighted(),
    "InverseVol": InverseVolatility(),
    "MinVariance": MeanRisk(objective_function=ObjectiveFunction.MINIMIZE_RISK, risk_measure=RiskMeasure.VARIANCE),
    "HRP-Variance": HierarchicalRiskParity(risk_measure=RiskMeasure.VARIANCE),
    "HRP-CVaR": HierarchicalRiskParity(risk_measure=RiskMeasure.CVAR),
    "HRP-CDaR": HierarchicalRiskParity(risk_measure=RiskMeasure.CDAR),
}

ANN = 252
print(f"\n{'model':<24}{'AnnRet':>8}{'AnnVol':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}")
print("-" * 63)
rows = {}
for name, model in models.items():
    pred = cross_val_predict(model, X, cv=wf, n_jobs=-1)
    r = np.asarray(pred.returns)
    ann_ret = r.mean() * ANN
    ann_vol = r.std() * np.sqrt(ANN)
    sharpe = ann_ret / ann_vol if ann_vol else 0.0
    eq = np.cumprod(1 + r)
    maxdd = float((eq / np.maximum.accumulate(eq) - 1).min())
    calmar = ann_ret / abs(maxdd) if maxdd else 0.0
    rows[name] = (ann_ret, ann_vol, sharpe, maxdd, calmar)
    print(f"{name:<24}{ann_ret:>7.1%}{ann_vol:>8.1%}{sharpe:>8.2f}{maxdd:>9.1%}{calmar:>8.2f}")

base = rows["EqualWeight (baseline)"]
print("\nΔ vs EqualWeight baseline:")
for name, (ar, av, sh, dd, cal) in rows.items():
    if name.startswith("EqualWeight"):
        continue
    print(f"  {name:<22} ΔSharpe {sh - base[2]:+.2f}   ΔMaxDD {dd - base[3]:+.1%}   ΔCalmar {cal - base[4]:+.2f}")
