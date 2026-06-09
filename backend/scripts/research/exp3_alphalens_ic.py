"""EXP3 — alphalens factor-vetting harness on the engine's core MR signal.

Demonstrates the research loop you'd run BEFORE wiring any factor into
cross_sectional_alpha_model.py: information coefficient (IC), IC decay across
horizons, quantile-spread returns, and factor turnover — all out of the box.

Factor tested: 5-day short-term reversal = -(P_t / P_{t-5} - 1), the literal
core of the MR thesis, evaluated cross-sectionally across the universe.
"""

from __future__ import annotations

import warnings

import numpy as np
from alphalens.performance import (
    factor_information_coefficient,
    factor_rank_autocorrelation,
    mean_return_by_quantile,
)
from alphalens.utils import get_clean_factor_and_forward_returns
from loader import close_panel, traded_tickers

warnings.filterwarnings("ignore")

panel = close_panel(traded_tickers()).dropna(axis=1, thresh=int(0.8 * 5139)).ffill()
# weekly sampling to cut overlap & speed alphalens; matches a swing cadence
panel_w = panel.resample("W-FRI").last().dropna(how="all")

reversal = -(panel_w / panel_w.shift(1) - 1.0)  # 1-week reversal
factor = reversal.stack()
factor.index = factor.index.set_names(["date", "asset"])

data = get_clean_factor_and_forward_returns(
    factor=factor,
    prices=panel_w,
    quantiles=5,
    periods=(1, 2, 4),  # 1/2/4 weeks ahead
    max_loss=0.5,
)

ic = factor_information_coefficient(data)
print("INFORMATION COEFFICIENT (Spearman factor vs forward return)")
print(f"  {'horizon':<10}{'mean IC':>10}{'IC std':>9}{'IR (IC/σ)':>11}{'t-stat':>9}")
for col in ic.columns:
    m, sd = ic[col].mean(), ic[col].std()
    ir = m / sd if sd else 0.0
    t = ir * np.sqrt(len(ic))
    print(f"  {col:<10}{m:>10.4f}{sd:>9.4f}{ir:>11.3f}{t:>9.1f}")

print("\nQUANTILE-SPREAD forward return (top quintile − bottom quintile, bps)")
mq, _ = mean_return_by_quantile(data, by_date=False)
for col in mq.columns:
    spread = (mq[col].iloc[-1] - mq[col].iloc[0]) * 1e4
    print(f"  {col:<10}{spread:>8.1f} bps")

print("\nFACTOR TURNOVER (rank autocorrelation; high=stable=cheap)")
ac = factor_rank_autocorrelation(data)
print(f"  mean rank autocorr (1 period): {ac.mean():.3f}")

print("\nRead: |IC| ~0.02-0.05 with t>2 = a usable cross-sectional factor.")
print("This is the per-factor screen to run on any candidate before wiring it.")
