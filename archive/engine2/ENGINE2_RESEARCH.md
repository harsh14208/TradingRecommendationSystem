# Engine 2 Research Report — Parallel Live Engine

**Goal:** Build a clean-sheet strategy in a parallel engine that achieves **per-trade Sharpe > 1**, without modifying the current live mean-reversion engine.

**Research date:** 2026-06-17
**Engine 1 baseline (legacy MR, v10.9 canon):** N=217, WR=69.1%, per-trade Sharpe=0.24, avg +0.61% (23-year IS, curated universe).

---

## 1. What was built

A new, isolated package was created under `backend/services/engines2/` and a standalone backtester under `backend/scripts/engine2_backtest.py`.  No files in the legacy engine were changed.

| Component | Path | Purpose |
|---|---|---|
| Engine 2 package init | `backend/services/engines2/__init__.py` | Public API: `generate_signal_tqm()` |
| TQM strategy | `backend/services/engines2/tqm_strategy.py` | Trend-Quality Momentum signal + simulation |
| TQM backtest | `backend/scripts/engine2_backtest.py` | Historical backtest, sweep mode, trade CSV output |

### Strategy: Trend Quality Momentum (TQM)

A long-only trend-continuation strategy designed to be orthogonal to the legacy MR engine.

* **Trend filters:** price > SMA200, SMA50 > SMA200, SMA200 rising.
* **Quality filters:** RSI 48–65, ADX ≥ 25, +DI > −DI, OBV > 20-day MA, MACD histogram positive and rising.
* **Entry trigger:** either a pullback to EMA20 or a breakout to a new 20-day high.
* **Relative strength:** within 15% of 52-week high, 63-day return positive vs SPY.
* **Risk:** ATR-based stop (default 1.75 ATR), target (4 ATR), trailing stop (2 ATR after 1 ATR profit), max hold 15 days.
* **Market regime:** SPY > SMA200, VIX ≤ 25.
* **Costs:** 0.50% round-trip friction, stop slippage 0.10% / gap 0.15%.

---

## 2. Backtest results

### 2.1 Engine 2 — TQM (full curated universe, 2003–2026)

```bash
cd backend && python scripts/engine2_backtest.py
```

| Metric | Value |
|---|---|
| Tickers tested | 111 |
| Trades | 163 |
| Win rate | 23.9% |
| Avg per trade | **−0.759%** |
| Avg win / avg loss | +4.539% / −2.426% |
| Profit factor | 0.59 |
| **Per-trade Sharpe** | **−0.19** |
| Portfolio CAGR (5% / trade) | −0.27% |
| Max drawdown | −6.07% |
| Avg hold | 5.6 days |
| Exit reasons | stop 70, time_loss 66, time 17, target 10 |

**Verdict:** The TQM strategy loses money after costs on the curated universe.  Most trades are stopped out or time-stopped flat.  The universe was selected for mean-reversion, so a trend-continuation rule set is structurally mismatched.

### 2.2 Engine 2 — TQM (tech-heavy subset, 2015–2024)

```bash
python scripts/engine2_backtest.py --tickers NVDA,MSFT,AAPL,GOOG,META,AMZN,NFLX,ADBE,INTC,AMD,QCOM,CSCO,CRM --start 2015-01-01 --end 2024-12-31
```

| Metric | Value |
|---|---|
| Trades | 17 |
| Win rate | 11.8% |
| Avg per trade | **−1.288%** |
| Per-trade Sharpe | **−0.28** |

**Verdict:** Even on the most momentum-friendly names, the strict pullback/breakout rules do not produce profitable trades at 0.5% round-trip friction.

### 2.3 Other quick-screened candidates

Several alternative rulesets were tested in throw-away notebooks.  None cleared zero per-trade Sharpe after 0.5% friction:

| Candidate | N (approx.) | WR | Avg/trade | Per-trade Sharpe |
|---|---|---|---|---|
| 20-day breakout, loose stops | 1,163 | 25.1% | −0.213% | −0.05 |
| SMA50 pullback in uptrend | 2,196 | 46.8% | −0.181% | −0.03 |
| Bollinger squeeze breakout | 1,394 | 44.3% | +0.015% | 0.00 |
| VIX-spike SPY mean-reversion | 77 | 49.4% | −0.210% | −0.04 |
| QQQ SMA200 trend | 68 | 25.0% | +4.460% | 0.26 |

### 2.4 Existing orthogonal candidate — Cross-sectional market-neutral alpha

The repo already contains a researched challenger model: `scripts/cross_sectional_alpha_model.py`.  It ranks the full S&P 500 cross-section and trades long/short deciles.  This is genuinely orthogonal to the legacy single-stock MR engine.

Fresh run (2019-01-02 → 2026-05-11 OOS, top/bottom 10%, 21-day rebalance):

| Metric | Value |
|---|---|
| Universe | 835 PIT single names |
| Rebalances | 89 |
| Ann. return **gross** | +4.43% |
| Ann. return **net** | +2.43% |
| Ann. volatility | 9.26% |
| Max drawdown | −17.49% |
| **Net Sharpe (annualized)** | **0.262** |
| Mean IC | +0.0024 |

**Verdict:** Positive net Sharpe, market-neutral by construction, but the gross spread is not large enough to overcome turnover costs.  Per-trade/ per-rebalance Sharpe is not reported by the script, but annualized Sharpe is far below 1.0.

---

## 3. Comparison table

| Engine / Strategy | Trades | WR | Avg/trade | Per-trade Sharpe | Annualized Sharpe | Edge? |
|---|---|---|---|---|---|---|
| Engine 1 (legacy MR, canon) | 217 | 69.1% | +0.61% | **0.24** | ~0.9–1.0 | ✅ Yes, validated |
| Engine 2 TQM | 163 | 23.9% | −0.76% | **−0.19** | — | ❌ No |
| Cross-sectional L/S | ~89 monthly rebalances | — | — | — | **0.26 net** | ⚠️ Marginal |

*Engine 1 annualized Sharpe is inferred from the portfolio simulation in `backtest_technicals.py` (`run_portfolio_simulation`).  Engine 2 TQM portfolio CAGR is negative.*

---

## 4. Why per-trade Sharpe > 1 is so hard here

Per-trade Sharpe = mean(net return) / std(net return).  To exceed 1.0, the average trade must be larger than the volatility of individual trade outcomes.

With the legacy MR engine already at **0.24**, quadrupling Sharpe requires one of:

1. **Higher win rate + better R:R.**  The current engine is 69% WR with ~1.33 R:R.  To reach Sharpe 1.0 would require roughly 85% WR at 2:1 R:R, or 75% WR at 3:1 R:R.  Neither has been found in any daily-bar equity strategy tested.
2. **Lower trade volatility.**  This means every trade must have a similar, small positive outcome — the profile of an options credit spread or high-frequency market-making strategy, not a directional equity swing strategy.
3. **Much larger average winner.**  Trend strategies can produce large winners, but they also produce many small losses, so per-trade Sharpe stays low (see QQQ trend result: 25% WR, +4.46% avg, Sharpe 0.26).

The curated universe itself is biased toward mean-reversion (that is why the legacy engine was built for it).  Trend, breakout, and squeeze rules fight the prevailing statistical behavior of these names.

---

## 5. Honest conclusion

**No clean-sheet daily-bar equity strategy tested in Engine 2 reaches a per-trade Sharpe above 1.0.**  The legacy MR engine remains the best-performing ruleset for this universe and data frequency.

The most promising **parallel** strategy is the existing **cross-sectional market-neutral model**, because:

* It is orthogonal to Engine 1 (long/short deciles vs single-stock MR).
* It is market-neutral, so it does not double up on equity beta.
* It has a positive net Sharpe, even if modest.

However, its current net Sharpe (0.26) is still far below 1.0.  The constraint is **turnover cost**, not signal absence: gross Sharpe is 0.48, but 10 bps one-way friction eats almost half the return.

---

## 6. Recommended next steps

If the goal remains Sharpe > 1, the realistic paths are:

### 6.1 Improve the cross-sectional model (best orthogonal candidate)

* Add stronger features (earnings surprise, analyst revisions, short-interest velocity, options-flow proxies).
* Move to a **quarterly rebalance (h=63)**.  Earlier research (`--nested-horizon`) found h=63 net Sharpe ~0.58, roughly double the h=21 result.
* Widen deciles or hold overlapping portfolios to cut turnover.
* Target: net annualized Sharpe 0.6–0.8.  Still not per-trade Sharpe > 1, but a genuinely additive second engine.

### 6.2 Meta-select the legacy MR engine’s best signals

Instead of a new alpha model, build Engine 2 as a **post-processor** that only forwards legacy Engine 1 signals when:

* Score band ≥ 65 (historically highest Sharpe band).
* Multiple MR triggers fire (RSI + BB%B + IBS).
* Calibrated probability is above a high threshold.
* Market regime is favorable (VIX 20–28, SPY > SMA200).

This keeps the proven MR edge but trades far less often and more selectively.  This is the fastest route to higher **per-trade** Sharpe, because it starts from an already-positive distribution.

### 6.3 Options / volatility strategies

A short-put-spread or iron-condor overlay on the same names can produce 70–80% win rates with small, consistent gains — the exact distribution needed for high per-trade Sharpe.  This requires historical options data and a separate backtest framework, but it is the most direct path to the stated > 1 per-trade Sharpe goal.

### 6.4 Do not deploy Engine 2 TQM live

The TQM module is preserved as a research artifact, but its current default parameters are not viable.  If you want to keep iterating on it, the next experiments should be:

* A different universe (full S&P 500, not the MR-curated list).
* Longer hold periods (30–60 days) with much wider stops.
* Intraday confirmation (e.g., close back above VWAP on the entry day).

---

## 7. Files created / modified

**Created (do not affect Engine 1):**

* `backend/services/engines2/__init__.py`
* `backend/services/engines2/tqm_strategy.py`
* `backend/scripts/engine2_backtest.py`
* `docs/ENGINE2_RESEARCH.md` (this file)

**Modified:** None in the live engine.

---

## 8. How to reproduce

```bash
cd /Users/harshv.singh/TradingRecommendationSystem/backend

# Engine 2 TQM — full universe
../.venv311/bin/python scripts/engine2_backtest.py

# Engine 2 TQM — subset
../.venv311/bin/python scripts/engine2_backtest.py \
  --tickers NVDA,MSFT,AAPL,GOOG,META,AMZN \
  --start 2015-01-01 --end 2024-12-31

# Cross-sectional market-neutral challenger
../.venv311/bin/python scripts/cross_sectional_alpha_model.py --split 2019-01-01
```
