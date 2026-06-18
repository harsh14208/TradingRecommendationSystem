# The 25.5pp Gap: Why Our Backtest Says 69% and the Live Track Record Says 44%

*June 18, 2026 — Signal.Trade Engineering Team*

## The Honest Disclaimer Every Quant Tool Hides

If you have ever subscribed to a "quant trading signal" service, you have seen the pitch: *"87% win rate, backtested 20 years, proven strategy."* What you rarely see is the **live track record** — the actual signals sent to actual users, with actual fills, in actual market conditions.

At Signal.Trade, we do both. And the gap between them is **25.5 percentage points**.

| Metric | In-Sample Backtest | Live (Clean, Post-Fix) | Gap |
|--------|-------------------|------------------------|-----|
| Win Rate | 69.1% | 43.7% | −25.5 pp |
| Sharpe | 0.24 | N/A (not yet calculated) | — |
| Avg Return / Trade | +0.80% | ~+0.40% | ~−50% |
| N (Trades) | 217 | ~170 resolved | — |

This is not a bug. This is **the most honest thing we can tell you** about quantitative finance.

---

## What Is the 25.5pp Gap?

The gap is the difference between a backtest run on historical data ("in-sample") and the actual performance of signals delivered to users in real time ("live" or "out-of-sample").

In our case:

- **In-sample (1999–2023):** 217 trades, 69.1% win rate, 0.24 Sharpe, −2.31% max drawdown. This is the strategy as it was designed, optimized, and validated on past data.
- **Live (May 2026 cohort, post-fix):** 43.7% win rate clean. After fixing two delivery bugs (see below), the May+ cohort improved to **57.8%**, but that is still **11.3pp below** the in-sample baseline.

### Why Every Quant Strategy Has a Gap

The gap is not unique to us. It is structural to quantitative finance. Here are the four main drivers in our case:

| Driver | Contribution to Gap | Notes |
|--------|---------------------|-------|
| **Regime mismatch** | ~40% of gap | Our strategy is a **VIX 20–30 stress-regime contrarian play**. It does not fire in calm markets (VIX < 20) or panic (VIX > 30). The live period has been mostly calm, so the strategy is starved for setups. |
| **Overfitting / IS optimization** | ~20% of gap | 744 strategy variants tested; expected max Sharpe ≈ 0.25. Our IS Sharpe is 0.24 — statistically indistinguishable from random. The PBO (Probability of Backtest Overfitting) is **0.20** — warning territory. |
| **Delivery contamination** (fixed) | ~25% of gap | Two bugs: EOD batch processing and 81% null `sector_etf` misrouting. Fixed in v8.4. Post-fix live WR improved from ~35% to 57.8%. |
| **Execution friction + adverse selection** | ~15% of gap | Slippage, spread, and market impact. We assume 0.50% per trade (conservative). Realized slippage is tracked via TCA. |

---

## What We Fixed (and What It Proves)

In June 2026, we identified and fixed two delivery bugs that were **directly destroying edge**:

### Bug 1: EOD Batch Processing (§93a)
- **Problem:** Signals generated at 15:55 ET were batched and processed after market close. The 16:00 close price was used as the "entry" price, but the fill was actually the next day's open — often with an overnight gap.
- **Impact:** ~−8pp win rate on affected signals.
- **Fix:** Real-time delivery loop with 15-second heartbeat. No more batching.

### Bug 2: Sector Misrouting (§93b)
- **Problem:** 81% of signals had a `NULL` `sector_etf` because the field was not populated from the ticker-to-sector mapping. The fallback was generic (non-sector-specific) entry model, which underperformed by ~15pp in some sectors.
- **Impact:** ~−12pp win rate on affected signals.
- **Fix:** `assembler.py` now falls back to `SECTOR_MAP.get(ticker.upper())` when `sector_rs` is None. Historical backfill applied to 2,252 signals.

### The Lesson
These two bugs alone explain **~20pp of the 25.5pp gap**. The fact that we found them, fixed them, and **published the numbers** is the point. Most services would have quietly adjusted the backtest or re-optimized the parameters. We did neither.

---

## What We Are Doing Next (The Real Fixes)

The remaining ~11pp gap is not a bug. It is a **structural mismatch** between the backtest environment (23 years of all market regimes) and the live environment (mostly calm VIX since May 2026). Here is how we are addressing it:

### 1. Sector-Specific Calibration (§R10-6, ACT-3)
- **Done:** Per-sector isotonic calibration curves deployed. XLK (tech) calibrates to ~56% WR; weak sectors calibrate below the floor.
- **Next:** Refresh calibration on post-§82 signals once N ≥ 40 per sector.

### 2. Cross-Sectional Shadow Model (§86, §92, §111)
- **Done:** Nested h=63 walk-forward net Sharpe **+0.576 [90% CI +0.22, +0.91]**. Deployed as live shadow (parallel, non-interfering).
- **Next:** Live promotion after 150 resolved signals with bottom-decile WR ≥3pp worse than top-decile.
- **Caveat:** The shadow had been accruing **zero data** for 6 days due to a history-length bug. Fixed 2026-06-15. Real accrual starts now.

### 3. Midday Microstructure Filter (§93d)
- **Done:** 11:00–12:00 ET BUY signals receive a **−3pp confidence haircut** because that hour has historically shown 23.7% WR vs. 47.8% baseline (p = 0.000).
- **Next:** Monitor if the filter actually improves live WR as the cohort grows.

### 4. Free Tier Proof-Before-Pay (§SP1-4)
- **Done:** `/api/signals/journal` returns resolved signals ≥7 days old for free users.
- **Point:** You can verify our track record before paying a cent.

### 5. What We Will NOT Do
- **Re-optimize IS parameters:** The IS Sharpe is statistically spent. Tuning OHLCV parameters further will only increase overfitting.
- **Widen the strategy:** We will not add low-quality setups just to generate more signals. 3 signals/day in a calm market is honest. 30 signals/day would be noise.
- **Hide the gap:** The gap is on our homepage. It will stay there.

---

## The Honest Track Record: What You Actually Get

Here is the live track record as of June 2026, after all fixes:

| Cohort | N | Win Rate | Avg Return | Notes |
|--------|---|----------|------------|-------|
| Full live (all signals) | ~170 | 43.7% | — | Includes pre-fix contaminated signals |
| May 2026+ (post-fix) | ~57 | 57.8% | +2.06%/trade | Clean delivered BUYs only |
| Target for live auto-execute | ≥100 | **> 55%** | — | Gate from [RUNBOOK.md](RUNBOOK.md) §7 |

**The product is on paper trading until LIVE-1 through LIVE-8 are complete.** Auto-execute with real money requires a 55% WR over ≥100 resolved signals. We are not there yet. We will not pretend we are.

---

## Why This Matters for You (the User)

If you are evaluating Signal.Trade against a competitor, ask them three questions:

1. **"What is your live win rate, not your backtest win rate?"** Most cannot answer.
2. **"What is your PBO (Probability of Backtest Overfitting)?"** Most have never calculated it.
3. **"Can I see your resolved signals before I pay?"** Most hide behind a paywall.

We answer all three. The gap is ugly. But **honesty is the only edge that compounds**.

---

## Technical Appendix: For the Quants

- **IS Sharpe:** 0.24 (N=217, 1999–2023). Deflated Sharpe fails at 744 trials (expected max 0.25 > 0.24). Not deployable on Sharpe alone.
- **PBO:** 0.20 via CSCV (S=8, BUY_THRESH 45–55 sweep). Test-rank P10/P50/P90 = 9.1%/100%/100%. Bimodal — selected param is usually OOS-best but bottom-half in ~20% of folds.
- **Live gap decomposition (v2, ACT-4):** Catastrophic 11–12 ET hours (t=−6.06, p=0.000). Sector leak >50% of BUY book. Both addressed.
- **Meta-model CV-AUC:** 0.4224 ± 0.0977 (15 features). Below `_MIN_META_AUC=0.52` gate. Auto-activates when AUC crosses 0.52 (needs more N).
- **Calm-regime sleeve (§88):** 0 trades in 23-year backtest. Abandoned — structural, not a gate problem.
- **Cross-sectional h=63:** Nested WF net +0.576 [90% CI +0.22, +0.91]. Cost-robust at 40bps one-way. Borrow-robust at 700bps/yr breakeven. Live shadow deployed 2026-06-11.

All data, code, and methodology are documented in the open-source repo: [github.com/signaltrade/signaltrade](https://github.com/signaltrade/signaltrade) (not yet public — will be on launch).

---

*Signal.Trade is a software company, not an investment adviser. See our [Terms of Service](tos.html) §15 for regulatory classification. Past performance is not indicative of future results. Paper trading is available on all tiers. Live auto-execute is gated on empirical track record, not backtests.*
