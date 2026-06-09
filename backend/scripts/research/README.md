# awesome-quant Tier-1 experiments

Prototypes that tested three libraries from
[awesome-quant](https://github.com/wilsonfreitas/awesome-quant) against the
engine's own data (`data/cache_ohlcv/`, `data/backtest_trades_is.csv`).
Run on 2026-06-09. All read the engine's real adjusted price history — no new data.

## ⚠️ Isolated env required

`skfolio` (via cvxpy) needs `numpy>=2.0`, which conflicts with the pinned
`numpy==1.26.4` in `backend/venv`, and `alphalens` drags
`empyrical-reloaded -> peewee<3.17.4` which breaks the `massive` client. **Never
install these into `backend/venv`.** Use a throwaway env:

```bash
python3.11 -m venv /tmp/venv_quant
source /tmp/venv_quant/bin/activate
pip install -r backend/scripts/research/requirements-research.txt
cd backend/scripts/research
python loader.py            # sanity-check the data panel
python exp1_skfolio_hrp.py  # skfolio HRP vs equal-weight
python exp2_garch_vol.py    # arch GARCH vs realized vol (~2 min)
python exp3_alphalens_ic.py # alphalens factor IC harness
```

`arch` on its own *is* numpy-1.26 safe and is already in `backend/requirements.txt`
(it powers `--barriers garch` in `train_metalabel_model.py`).

## Results & verdicts

| Exp | Library | Finding | Verdict |
|---|---|---|---|
| 1 | **skfolio** | On the long-only large-cap universe, equal-weight beats HRP on Sharpe (0.98 vs 0.96) and Calmar; HRP only trims ~3pp MaxDD. Min-var worse. | **DEFER** — re-test on the cross-sectional L/S decile book once `cross_sectional_alpha_model.py` emits real weights; no edge on the long book. |
| 2 | **arch** | GARCH(1,1) forecasts forward 10d vol better than trailing realized (Spearman ρ +0.027, RMSE −0.050). Vol-targeting Sharpe 0.94→0.96 with ~22% tighter risk control (vol-of-vol 0.069→0.054). | **GO (sizing layer)** — modest. Wired as `--barriers garch` in the meta-label labeler (default off; ablation showed ΔAUC≈0 for *barriers* specifically — the edge is in vol-targeting/sizing, not barrier width). |
| 3 | **alphalens** | Core 1-week reversal factor: IC 0.024 (t=4.0), IC decays with horizon, rank-autocorr ≈ −0.02 (brutal turnover). Surfaced all three diagnostics in seconds. | **ADOPT (research only)** — the per-factor screen to run before wiring anything into the cross-sectional model. Stays in this isolated env. |

`exp1b_skfolio_neutral.py` is a degenerate control (equal-weight of residual
returns ≈ 0); kept for reference, not a usable test without an alpha overlay.
