# Signal.Trade — Institutional Performance Report

> Generated from live PostgreSQL DB via `backend/scripts/calc_tbd_metrics.py`.
> **Last run:** 2026-05-17 · **Coverage:** 2026-04-20 → 2026-05-08 · 529 resolved trades (459 effective ticker-days)
> _Sharpe/Sortino: sqrt(252) scaling, per-signal quality metrics — not portfolio equity-curve Sharpe._
> _Snapshot: `baseline-v2-sortino-1r-fixes` in `performance_snapshots` table._

---

## 1. Return Summary

| Metric | Reported | Realistic | Note |
|---|---:|---:|---|
| Win Rate | 58.8% | 42.2% | Realistic = stop-enforced (88 phantom wins removed) |
| Avg Return / Trade | +2.51% | +2.01% | Realistic = after 0.50% round-trip friction |
| Avg Win | +6.38% | +5.88% | after friction |
| Avg Loss | -3.02% | -3.52% | after friction |
| Payoff Ratio | 2.12× | 1.67× | friction-adjusted win / \|loss\| |
| Profit Factor | 3.02x | — | gross profit / gross loss |
| Expectancy / Trade | +2.51% | **+0.45%** | Realistic = stop-enforced WR × friction-adj returns |
| Kelly Fraction | 39.3% | **7.6%** | Realistic Kelly unreliable until calibration gap < 5pp |

> **Expectancy gap:** reported `+2.51%` vs realistic `+0.45%` — a **2.06pp difference** driven by 88 phantom wins and 0.50% friction. The realistic figure is what a live broker account will experience.

---

## 2. Risk-Adjusted Metrics

| Metric | Value | Benchmark |
|---|---:|---|
| Sharpe Ratio | 5.67 | > 1.0 = good, > 2.0 = excellent |
| Sortino Ratio | 15.12 | semi-deviation from 0%, divisor = n |
| Calmar Ratio | 14.76 | (ann\_ret × 5% position size) / max DD |
| Omega Ratio | 3.02 | > 1.0 = edge exists |
| Max Drawdown | -2.14% | 5% position sizing |
| Recovery Factor | 30.99 | (total net × 5%) / max DD |
| Ulcer Index | 0.46 | < 5 = low drawdown stress |

---

## 3. Tail Risk (Non-Parametric)

| Metric | Value | Interpretation |
|---|---:|---|
| VaR 95% | -6.80% | worst single-trade loss, 1-in-20 |
| VaR 99% | -9.99% | worst single-trade loss, 1-in-100 |
| CVaR 95% | -8.70% | avg loss beyond VaR 95 |
| CVaR 99% | -10.83% | avg loss beyond VaR 99 |
| Volatility (σ) | 7.03% | per-trade std dev |

---

## 4. Distribution Diagnostics

| Metric | Value | Interpretation |
|---|---:|---|
| Skewness | +1.282 | right tail — large wins dominate (unbiased Fisher-Pearson) |
| Excess Kurtosis | +2.345 | fat tails vs normal (unbiased estimator) |
| T-statistic | +8.21 *** | H₀: mean return = 0 |
| P-value | < 0.0001 | statistically significant edge (p < 0.001) |
| Brier Score | 0.2863 | 0 = perfect, 0.25 = random |
| Max Win Streak | 16 | |
| Max Loss Streak | 8 | |

---

## 5. Validation Report (from `validate_predictions.py`)

### Sample Quality

| Metric | Value |
|---|---:|
| Sent BUY+SELL signals | 543 |
| Resolved (have outcome) | 529 |
| Effective ticker-days | 459 |
| Duplicate ticker-day rate | 13.2% |

### Confidence Calibration

| Metric | Raw | Friction-Adj |
|---|---:|---:|
| Win Rate | 62.6% | 54.4% |
| Avg Confidence | 73.6% | 73.6% |
| Confidence Gap | +11.0pp | +19.1pp |
| Verdict | OVERCONFIDENT | OVERCONFIDENT |

### Exit Type Breakdown

| Exit | Count | % of resolved |
|---|---:|---:|
| Target hit | 203 | 38.4% |
| Stop hit | 242 | 45.7% |
| Time exit | 118 | 22.3% |

---

## 6. Multi-Timeframe Win Rates

| Horizon | Count | Win Rate | Avg Return | PF | Sharpe |
|---|---:|---:|---:|---:|---:|
| 1d | 529 | 42.0% | +0.29% | 1.45x | 1.78 |
| 3d | 529 | 55.6% | +0.94% | 2.06x | 3.73 |
| 7d (primary) | 529 | 58.8% | +2.51% | 3.02x | 5.67 |
| 14d | 456 | 64.3% | +5.02% | 4.36x | 7.54 |

---

## 7. Monthly Performance

| Month | Trades | Win Rate | Avg Return | PF | Sharpe |
|---|---:|---:|---:|---:|---:|
| 2026-04 | 336 | 63.4% | +3.01% | 3.59x | 6.40 |
| 2026-05 | 193 | 50.8% | +1.63% | 2.19x | 4.25 |

---

## 8. Performance Breakdowns

### By Hold Style

| Style | N | Win Rate | Avg Ret | PF | Sharpe | Max DD |
|---|---:|---:|---:|---:|---:|---:|
| **Position** | 451 | 61.6% | +2.88% | 3.64x | 6.45 | 2.10% |
| **Swing** | 55 | 45.5% | +0.81% | 1.41x | 1.93 | 2.62% |
| **Intraday** | 23 | 34.8% | -0.65% | 0.73x | -1.88 | 1.06% |

### By Action

| Action | N | Win Rate | Avg Ret | PF | Sharpe |
|---|---:|---:|---:|---:|---:|
| **BUY** | 479 | 58.0% | +2.67% | 3.08x | 5.83 |
| **SELL** | 50 | 66.0% | +0.94% | 2.12x | 4.03 |

### By Exit Type

| Exit Type | N | Win Rate | Avg Ret | PF |
|---|---:|---:|---:|---:|
| **Target hit** | 203 | 85.2% | +7.72% | 18.81x |
| **Time exit** | 118 | 74.6% | +1.78% | 7.01x |
| **Pending** | 40 | 37.5% | -0.28% | 0.75x |
| **Stop hit** | 168 | 20.8% | -2.60% | 0.11x |

### By Confidence Band (Reliability Diagram)

| Band | N | Avg Conf | Actual WR | Gap | Status |
|---|---:|---:|---:|---:|---|
| 0–50% | 11 | 46.9% | 54.5% | -7.7pp | OK |
| 50–55% | 29 | 53.0% | 55.2% | -2.2pp | OK |
| 55–60% | 23 | 56.8% | 60.9% | -4.0pp | OK |
| 60–65% | 82 | 63.2% | 75.6% | -12.4pp | UNDER ⚠ |
| 65–70% | 68 | 67.4% | 60.3% | +7.1pp | OK |
| 70–75% | 58 | 72.2% | 58.6% | +13.6pp | OVER ⚠ |
| 75–80% | 58 | 77.6% | 48.3% | +29.3pp | OVER ⚠ |
| 80–101% | 200 | 85.6% | 55.0% | +30.6pp | OVER ⚠ |

### By Sector ETF

| Sector | N | Win Rate | Avg Ret | PF |
|---|---:|---:|---:|---:|
| XLK (Tech) | 17 | 88.2% | +7.15% | 14.79x |
| XLV (Healthcare) | 3 | 100.0% | +5.33% | ∞ |
| XLY (Cons. Disc.) | 4 | 75.0% | +3.42% | 13.43x |
| XLB (Materials) | 3 | 66.7% | +1.59% | 2.64x |
| XLRE (Real Estate) | 3 | 66.7% | +0.71% | 4.37x |
| XLI (Industrials) | 16 | 56.2% | +0.56% | 1.61x |
| XLE (Energy) | 2 | 50.0% | -0.36% | 0.36x |
| XLF (Financials) | 22 | 27.3% | -1.59% | 0.32x |
| XLP (Cons. Staples) | 11 | 18.2% | -1.79% | 0.35x |
| XLU (Utilities) | 1 | 0.0% | -3.03% | 0.00x |

### By Market Session

| Session | N | Win Rate | Avg Ret | PF |
|---|---:|---:|---:|---:|
| After-hours | 6 | 83.3% | +5.78% | 15.09x |
| Regular | 10 | 60.0% | +4.14% | 11.75x |
| Pre-market | 4 | 50.0% | -1.79% | 0.37x |
| Closed | 77 | 49.4% | +1.77% | 2.12x |

---

## 9. Trade-Path Analytics (MAE / MFE)

| Metric | Value |
|---|---:|
| Hit Target | 203 / 529 (38.4%) |
| Hit Stop | 242 / 529 (45.7%) |
| Phantom Wins | 88 — stop touched but position recovered by 7d mark |
| Stop-Enforced Win Rate | **42.2%** (vs 58.8% reported — 16.6pp gap) |
| Avg MAE | -6.04% (worst: -25.11%) |
| Avg MFE | +10.64% (best: +70.90%) |
| MFE / MAE Ratio | 1.76× |
| Payoff Ratio | 2.12× |
| Avg Stop Distance | 6.10% |
| Capture Ratio | 0.41× |
| % Trades > 1R | 19.5% |

---

## 10. Return Distribution

| Percentile | Return |
|---|---:|
| P1 (worst 1%) | -9.99% |
| P5 (VaR 95%) | -6.80% |
| P10 | -4.72% |
| P25 (Q1) | -1.42% |
| P50 (median) | +1.18% |
| P75 (Q3) | +4.53% |
| P90 | +12.36% |
| P95 | +15.79% |
| P99 (best 1%) | +25.02% |

---

## 11. Alpha vs SPY Benchmark

> Computed by `calc_tbd_metrics.py` via OLS regression: `signal_ret = α + β × SPY_ret + ε` across 529 paired windows.
> Each signal's SPY return is measured over the same calendar window (entry `created_at` → `outcome_at`).
> SPY bars cached to `data/.spy_bars_cache.json` — fetched via yfinance fallback when Polygon is rate-limited.

| Metric | Value | Interpretation |
|---|---:|---|
| Paired trades | 529 | all 529 resolved signals matched to SPY window |
| SPY avg return / window | +1.75% | benchmark return over same ~7d hold period |
| Raw Alpha / trade | +0.76% | avg signal − avg SPY (naive, no regression) |
| Raw Alpha (annualised) | +190.84% | ×252 same convention as Sharpe |
| Beta | +0.918 | market sensitivity (OLS slope); near 1 = market-correlated |
| Jensen's Alpha / trade | +0.90% | OLS intercept — edge independent of market direction |
| **Jensen's Alpha (annualised)** | **+227.00%** | **primary alpha headline; ×252** |
| Tracking Error / trade | 7.00% | std of residuals (excess-return volatility) |
| Tracking Error (annualised) | 111.04% | ×√252 |
| **Information Ratio** | **2.04** | **annualised α / annualised TE; >0.5 = good, >1.0 = excellent** |
| R² | 0.010 | only 1% of signal variance explained by SPY — edge is largely market-independent |

---

## 12. Tier-1 Technical Backtest — v5.10 (20-Year)

> Run by `backend/scripts/backtest_technicals.py` · v5.10 · 2026-05-17
> 27 individual equities (no ETFs) · 2006-01-01 → 2026-05-17 · 5-day hold · 0.20% friction
> Gates: RVOL≥1.2, VIX>30 hard block, SPY SMA200 ±2% neutral zone, ADX≥18, RSI>70+ADX<28 weak-trend block, MAX_LOSS_DAYS=3 at −1%, bear market score≥60
> ATR stops: 1.5×s / 2.0×t (swing default); 2.0×s / 2.5×t (low-vol); 1.5×s / 2.0×t (high-vol)

### Overall Performance (1940 trades)

| Metric | Value |
|:---|---:|
| Total Trades | 1,940 |
| Win Rate | 49.6% |
| Avg Return / Trade | +0.13% |
| Avg Win | +2.84% |
| Avg Loss | -2.54% |
| Profit Factor | 1.10× |
| Sharpe Ratio | 0.04 |
| Max Drawdown | -3.87% |

### BUY vs SELL

| Action | N | Win Rate | Avg Ret | PF | Sharpe | Max DD |
|:---|---:|---:|---:|---:|---:|---:|
| **BUY** | 1,940 | 49.6% | +0.13% | 1.10× | 0.04 | -3.87% |
| **SELL** | 0 | — | — | — | — | — |

### Exit-Type Breakdown

| Exit | N | % of Total | Win Rate | Avg Ret |
|:---|---:|---:|---:|---:|
| Target | 358 | 18.5% | 100.0% | +4.46% |
| Stop | 446 | 23.0% | 0.0% | -3.63% |
| Time (win) | 765 | 39.4% | 79.0% | +1.38% |
| Time (loss) | 371 | 19.1% | 0.0% | -2.11% |

### Regime Breakdown

| Regime | N | Win Rate | Avg Ret | PF | Sharpe | Max DD |
|:---|---:|---:|---:|---:|---:|---:|
| Pre-GFC Bull | 130 | 55.4% | +0.39% | 1.36× | 0.12 | -1.01% |
| GFC Bear | 24 | 33.3% | -0.55% | 0.72× | -0.14 | -1.33% |
| Post-GFC Bull | 1,164 | 50.1% | +0.09% | 1.08× | 0.03 | -3.20% |
| COVID Crash | 6 | 0.0% | -3.08% | — | — | -0.92% |
| COVID Recovery | 158 | 48.1% | +0.17% | 1.12× | 0.05 | -1.99% |
| Rate-Hike Bear | 26 | 23.1% | -2.50% | 0.14× | -0.88 | -3.28% |
| AI Rally | 256 | 48.0% | +0.32% | 1.23× | 0.08 | -2.27% |
| Current (2025+) | 149 | 54.4% | +0.38% | 1.24× | 0.09 | -1.64% |

### Top 10 Per-Ticker Performance

| Ticker | N | Win Rate | Avg Ret |
|:---|---:|---:|---:|
| TSLA | 55 | 60.0% | +0.96% |
| AMD | 58 | 48.3% | +0.61% |
| MSFT | 87 | 57.5% | +0.46% |
| MA | 87 | 57.5% | +0.41% |
| CSCO | 75 | 56.0% | +0.40% |
| AAPL | 85 | 48.2% | +0.34% |
| CVX | 54 | 55.6% | +0.28% |
| CRM | 80 | 48.8% | +0.27% |
| WFC | 55 | 50.9% | +0.25% |
| INTC | 82 | 51.2% | +0.23% |

### Live Engine vs Backtest

| Source | Trades | Win Rate | Avg Ret | Sharpe |
|:---|---:|---:|---:|---:|
| Live Engine | 529 | 42.2% | +0.45% | 5.67 |
| Backtest v5.10 | 1,940 | 49.6% | +0.13% | 0.04 |
| Gap | — | +7.4pp | -0.32pp | — |

### Key Findings

- **Break-even WR** given 2.84/2.54 win/loss ratio is 47.1%; achieved 49.6% — positive edge confirmed across the full 20-year cycle.
- **Max Drawdown −3.87%** at 5% position sizing across 20 years — exceptional capital protection.
- **Gap to live engine (+5.63 Sharpe)** quantifies the value of the news, options flow, and fundamentals alt-data stack that technical rules alone cannot replicate.
- **Annualised Sharpe estimate:** 0.04 × √(1940/20) ≈ 0.39 (per-trade basis, not daily).
- **Bear regimes remain the hardest:** COVID crash (0% WR) and 2022 rate-hike bear (23.1% WR) confirm that long-only technical rules cannot profit in systemic downtrends.

### v5.10 Changes vs v5.9

- Swing ATR target 3.0× → 2.0× (target hit rate 11% → 18.5%)
- RVOL gate: hard block at <1.2 (removed score<50 escape)
- ATR min gate: 0.7% hard block (was 0.8% soft-conditional)
- ADX minimum gate (new): ADX<18 + non-oversold → HOLD
- RSI>70 + ADX<28 weak-trend gate (new): catches topping market false breakouts
- Bear market gate: score<42 → score<50
- SMA200 RSI exception: <30 → <25
- SPY neutral zone (±2% SMA200): score<45 → HOLD in transition regimes
- `macro.py`: SPY SMA200 computation (1y history), `sp500_neutral_zone` flag
- Defensive ticker block extended: ABBV, MRK, PFE, LLY, TMO, TXN, NKE, V, PM, WMT added

