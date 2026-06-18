# Signal.Trade — Quantitative Edge Assessment
## A Rigorous Analysis of Signal Profitability, the Live-vs-IS Gap, and Path to Viable Alpha

**Analyst:** Quantitative Researcher (External Lens)
**Date:** 2026-06-15
**Classification:** Internal — Strategic & Risk Assessment
**Version:** v1.0 (Synthesis of v8.4–v10.10 evidence base)

---

## Executive Summary

### The Bottom Line

**Would I invest my own money in Signal.Trade today?** No — not at meaningful size. The strategy shows *genuine* idiosyncratic alpha (factor attribution: +0.87%/day, p=0.044, R²=0.05), but the current live edge is too thin, too regime-dependent, and too contaminated by unresolved structural issues to justify capital deployment beyond a small, tightly-capped research allocation.

**In 6 months?** Maybe — if three conditions are met: (1) the post-fix forward window (clean delivery, no sector leaks, no SELL bypass) accrues ≥150 resolved signals with net WR consistently >55%, (2) the cross-sectional shadow (h=63) proves it can add orthogonal portfolio-level Sharpe, and (3) a paid alt-data source (options flow or VRP) demonstrates pre-registered edge in a forward SPRT test. Absent those, the strategy remains a research curiosity, not a product.

### Honest Expected Returns (Net of All Costs)

| Scenario | Per-Trade Sharpe | Ann. Sharpe (est.) | Net WR | Avg Return/Trade | Confidence |
|---|---|---|---|---|---|
| **Optimistic** (post-fix clean book + h=63 shadow + sector models) | 0.35–0.45 | 1.2–1.6 | 58–62% | +1.2–1.8% | Low — requires 3 unproven levers |
| **Base Case** (current clean book, no new data) | 0.20–0.28 | 0.6–0.9 | 52–57% | +0.8–1.2% | Moderate — May+ N=90 is clean but small |
| **Pessimistic** (regime persists, no shadow, delivery decay) | 0.08–0.15 | 0.2–0.4 | 45–50% | +0.2–0.6% | Moderate-High — 2022+ epoch Sharpe = −0.10 |
| **Breakeven** (after 0.50% friction + slippage) | ~0.10 | ~0.3 | ~50% | ~+0.5% | — |

> **Critical caveat:** The IS canon (N=217, WR=69.1%, Sharpe=0.24) is **statistically spent** — deflated Sharpe FAILS at the honest 744-trial count (E[max SR]=0.25 > 0.24). The IS lever cannot be trusted for forward expectations. All edge proof must come from live/OOS data.

---

## 1. Honest Assessment: Can This Strategy Make Users Money?

### 1.1 The Case FOR an Edge

Signal.Trade is not a random-number generator. The evidence for genuine alpha is real and unusually well-documented for a retail-grade system:

| Evidence | Statistic | Interpretation |
|---|---|---|
| Factor attribution (FF5 + ST_Rev) | Alpha +0.87%/day, p=0.044 | Genuine idiosyncratic alpha, not factor replication |
| R² (FF5 + ST_Rev) | 0.05 (95% idiosyncratic) | Edge is not "market went up" |
| 23-year backtest | Positive Sharpe in 5/6 regimes | Survives GFC, COVID recovery; fails rate-hike bear |
| Clean live book (May+ post-fix) | 57.8% WR, +2.06%/trade net | Delivery-leak-corrected live alpha is near-IS |
| Cross-sectional shadow (h=63) | Net Sharpe +0.576 [CI +0.22, +0.91] | Portfolio-level orthogonal edge exists, selection-clean |
| Information Ratio | 2.04 | Excellent alpha per unit tracking risk |

**The mechanism is structurally sound:** The strategy buys quality large-caps after forced-selling dislocations (VIX 20–30 stress regime) and captures the microstructure correction. This is not pattern-fitting — it exploits a real market dynamic (ETF rebalancing cascades, stop clusters, institutional redemptions).

### 1.2 The Case AGAINST Deployment Today

| Problem | Evidence | Severity |
|---|---|---|
| **Live WR below breakeven** | 42.5% phantom-corrected (58.8% raw) | **Critical** — below 50% coin-flip after stops |
| **Regime dependence** | 100% of trades in VIX 20–30; post-2022 Sharpe = −0.10 | **Critical** — live period overlaps negative regime |
| **IS statistical budget spent** | DSR fails at 744 trials; E[max SR]=0.25 > IS 0.24 | **Critical** — cannot iterate IS further |
| **25.5pp live-vs-IS gap** | 43.6% live vs 69.1% IS | **Critical** — even post-fix, gap is regime-driven |
| **Midday microstructure catastrophe** | Hour 11–12 ET: WR 23.7% vs 47.8% baseline (p=0.000) | **High** — unfiltered, destroys edge in real-time |
| **Meta-model disabled** | CV-AUC 0.4364 < 0.52 gate; auto-OFF | **High** — no ML-based confidence scaling |
| **Calibration stage mismatch** | Trained on final conf, applied mid-pipeline | **Medium** — isotonic-on-isotonic feedback loop |
| **Per-ticker blocks on N=4** | APH blocked on 4 live trades = online noise-fitting | **Medium** — overfitting to tiny samples |
| **OOS-ALL Sharpe** | 0.04–0.05 (honest generalization) | **Medium** — near-zero out-of-sample |
| **Concurrent MaxDD** | −7.06% at 5-slot sizing (vs −0.85% per-trade) | **High** — risk is 8× worse than per-trade metrics suggest |

### 1.3 The Verdict

> **The edge is real but the product is not yet investable.**

The strategy has passed the first hurdle — proving alpha exists — but failed the second: proving it is robust, scalable, and profitable under live conditions net of all costs. The clean post-fix book (57.8% WR, N=90) is encouraging but statistically thin. The 2022+ rate-hike epoch is structurally hostile to this mean-reversion setup, and there is no evidence the strategy can adapt to that regime without orthogonal data.

**My personal recommendation threshold:** I would consider a small allocation (1–2% of risk capital) only after:
- ≥150 post-fix resolved signals with net WR > 55% (not 57.8% on N=90)
- Brier score < 0.22 (currently 0.2641 — still 11pp overconfident)
- Midday 11–12 ET effect either confirmed dead or hard-filtered
- Cross-sectional shadow (h=63) promoted with ≥100 tagged signals showing bottom-decile underperformance

---

## 2. The REAL Expected Sharpe / Return for Users

### 2.1 Net-of-Everything Per-Trade Economics

| Line Item | Value | Source |
|---|---|---|
| Gross avg return / trade (IS) | +0.80% | v10.9 canon, N=217 |
| Round-trip friction (assumed) | −0.50% | Conservative at ≥$50M ADV |
| **Net avg return / trade** | **+0.30%** | IS baseline |
| Net avg return (clean live May+) | +2.06% | N=90, post-fix |
| Net avg return (phantom-corrected live) | +0.10% | 543 trades, Apr–May 2026 |
| Per-trade volatility | 7.03% | Live sample |
| **Per-trade Sharpe (net)** | **0.30 / 7.03 ≈ 0.04** | Phantom-corrected live |
| **Per-trade Sharpe (clean post-fix)** | **2.06 / 7.03 ≈ 0.29** | N=90, May+ only |

The phantom-corrected live Sharpe of **1.32** (per-trade, not portfolio) is misleading — it reflects the 42.5% WR and the right-tail convexity of the target/stop ratio (2:1), not sustainable risk-adjusted returns. At portfolio level, the concurrent MaxDD of −7.06% means the effective Sharpe is much lower.

### 2.2 Portfolio-Level Reality

The per-trade Sharpe is not what users experience. Users experience:

- **5 concurrent slots** (typical portfolio sizing)
- **Correlation between positions**: ~0.3–0.5 in stress regimes (same-sector clusters)
- **Drawdown**: Concurrent MaxDD = −7.06% (not the per-trade −0.85%)
- **Annualized Sharpe estimate**: Per-trade Sharpe × √(N/20) × portfolio_dampener

| Config | Per-Trade Sh | Est. Trades/Year | Portfolio Ann.Sh (theoretical) | Portfolio Ann.Sh (realistic, DD-adjusted) |
|---|---|---|---|---|
| IS canon (v10.9) | 0.24 | ~115 | 0.34 | 0.25–0.30 |
| Clean live (May+, N=90 annualized) | 0.29 | ~90 | 0.39 | 0.28–0.35 |
| Phantom-corrected full live | 0.04 | ~115 | 0.06 | ~0.00–0.05 |
| Cross-sectional shadow (h=63) | 0.576 | 4 quarterly rebalances | 0.576 | 0.45–0.55 |

**Realistic user expectation today:** 0.20–0.35 annualized Sharpe if the clean post-fix book persists; 0.00–0.10 if the phantom-corrected regime is the truth. The honest interval is wide because the sample is small and the regime is hostile.

### 2.3 Slippage and Hidden Costs

| Cost Category | Assumption | Evidence |
|---|---|---|
| Round-trip friction | 0.50% | Defensible for large-cap, but thin for gap-throughs |
| Gap-through stop slippage | 0.15% (assumed) | Likely 0.30–0.50% on earnings gaps; earnings blackout uses wrong dates |
| Broker commission | $0 (Alpaca/IBKR) | Verified |
| Borrow cost (if short enabled) | N/A | SELLs disabled |
| Market impact | Negligible at small size | No impact model; fine at 5% position size |
| TCA slippage (live) | Unknown | Zero fills recorded in ledger; 0.5% is deliberate 2× conservative buffer |

**Bottom line:** The 0.50% friction assumption is conservative for normal fills but may understate true costs by 0.20–0.40% on gap-through stop days. The net-of-friction calibration (v4, Brier 0.2641) is directionally correct but the stage-mismatch issue means confidence values are still somewhat distorted.

---

## 3. Deep Analysis: The Live-vs-IS Win-Rate Gap

### 3.1 Gap Decomposition

**The gap:** 25.5 percentage points (IS 69.1% vs live 42.5% phantom-corrected).

| Component | Estimated pp Contribution | Evidence | Fixable? |
|---|---|---|---|
| **1. Regime mismatch (primary)** | ~12–15 pp | Live period = 2022+ rate-hike epoch; backtest Sharpe = −0.10 in that regime. 100% of trades in VIX 20–30; post-2022 is hostile. | **Partially** — requires regime switching or orthogonal data |
| **2. Delivery leaks (fixed 2026-06-10)** | ~8–10 pp | Sector model-file unblock (32% of book at −1.4%/trade), SELL bypass (35.2% WR), null sector_rs (81% of signals), stale EOD misconfounded | **Fixed** — clean book now 57.8% WR |
| **3. Midday microstructure (11–12 ET)** | ~3–4 pp | WR 23.7% vs 47.8% baseline (p=0.000). Scanner warning added, no hard filter yet. | **Unknown** — May+ cohort shows reversal (N=4, WR=75%), may be regime-specific |
| **4. Data snooping / overfitting** | ~2–3 pp | PBO=0.200 (>0.15 warning); DSR fails at 744 trials; 300+ effective searches | **Not fixable** — IS ceiling is spent |
| **5. Implementation / live-backtest distribution gap** | ~1–2 pp | Live indicators use intraday partial bars vs backtest completed daily bars; fill at next-open vs intraday delivery | **Partially** — close-entry A/B neutral (ΔSharpe 0.00) |
| **6. Fundamental modifier misfire** | ~1–2 pp | §50/§51/§52/§73/§74/§76 applied live but not in IS; some may be noise | **Fixable** — §85-1 audit at ≥200 resolved signals |
| **7. Meta-model train/serve skew** | ~0–1 pp | Meta-model disabled (CV-AUC 0.4364), so no live scaling; but if enabled, would have been noise | **Mitigated** — disabled via AUC gate |

**Total explained:** ~27–35 pp (the components overlap; the 25.5pp gap is the net). The honest conclusion is that **~60% of the gap is structural (regime + overfitting) and ~40% was fixable delivery contamination.**

### 3.2 Which Delivery Fixes (v8.4) Actually Moved the Needle?

| Fix | Impact | Evidence |
|---|---|---|
| **Sector model-file unblock removed** | **Largest single fix** | XLF/XLP/XLI were 32% of book at ≈−1.4%/trade; removing them lifted blended WR from ~43% to ~57% |
| **SELL delivery disabled** | Moderate | 71 SELLs at 35.2% WR, −1.00%/trade were pure drag |
| **sector_rs couplings decoupled** | Moderate | 81% of signals had null sector_rs, disabling per-sector calibration; fallback to SECTOR_MAP restored it |
| **§55/§14 hard blocks removed** | Small-to-moderate | Fresh canon A/B showed §14 harmful (−0.06 Sharpe) — but this was later **retracted** (FRED panel was dead during measurement); honest §14 reads +0.03 Sharpe |
| **DELIV-1 entry-validity guard** | Small | Replaced age-based cutoff with price-based guard; protects followers from price-escaped entries |
| **skip_reason persisted** | Observational | Enables future audit, no direct WR impact |

**The v8.4 delivery audit was a success:** It proved that live alpha was *near-IS all along* — the delivery infrastructure was leaking it. The clean book (57.8% WR, +2.06%/trade) is close to the IS 69.1% once you account for the regime mismatch. This is the most important finding in the project's recent history: **the signal is better than the delivery made it look.**

### 3.3 What Else Needs Fixing?

| Issue | Fix | Urgency | Effort |
|---|---|---|---|
| **Midday 11–12 ET filter** | Hard block or confidence haircut for signals generated in that window | High | Low (1 day) |
| **Per-ticker adaptive blocks on N<30** | Replace per-ticker live blocks with hierarchical shrinkage or hard N≥30 rule | High | Medium |
| **Calibration stage mismatch** | Persist raw_confidence; calibrate as last pipeline step; align win label to 10d net-of-friction | Medium | Medium |
| **Publication-lag FRED series** | Shift STLFSI4/NFCI by 7 days; re-run canon | Medium | Low |
| **Survivorship bias** | Norgate/Sharadar PIT data (~$20–33/mo) or quantify bound | Medium | Low (paid) |
| **OOS-ALL generalization** | Pre-specified v7/v8/v9 ticker accrual; honest OOS Sharpe | High | Wait-only |
| **Fill-quality telemetry** | Per-trade signal-price vs broker-fill distribution | Medium | Medium |
| **Portfolio-level MAE/CVaR** | Track intra-trade MTM excursions; report worst-5 trades | Medium | Medium |
| **Meta-model stable retrain** | Accumulate N until CV-AUC crosses 0.52 (~4–6 months) | Medium | Wait-only |
| **Champion/challenger frozen window** | Score both models on same evaluation window | Medium | Medium |

---

## 4. Most Promising Paths to Genuine Edge Improvement

### 4.1 Ranked Opportunity List

| Rank | Opportunity | Expected Impact | Timeline | Feasibility | Key Risk |
|---|---|---|---|---|---|
| **1** | **Cross-sectional shadow promotion (h=63)** | +0.30–0.50 portfolio Ann.Sharpe | 2–3 months | **High** | Needs ≥150 tagged signals; h=63 shadow was broken (1y→2y fetch) until 2026-06-12 |
| **2** | **Sector-specific models (XLF/XLP/XLU/XLI)** | +3–5 pp WR per sector if validated | 3–4 months | **Medium** | §117 infrastructure complete; no model trained yet. Need ≥100 backtest trades/sector + OOS AUC ≥0.55 |
| **3** | **Paid options flow / VRP / GEX (Unusual Whales, ORATS)** | +0.15–0.25 Sharpe if signal is real | 2–3 months | **Medium** | No free-data path has cleared IC>0.03; paid data may also fail. Requires SPRT pre-registration |
| **4** | **Midday 11–12 ET hard block** | +3–5 pp WR if effect is persistent | 1 week | **High** | May+ cohort shows reversal (N=4); may be regime-specific, not structural |
| **5** | **Execution optimization (limit orders, close-entry)** | ΔSharpe ≈ 0.00 (close-entry); limit orders fail deploy bar | 1–2 months | **Low** | §97a limit grid all failed (adverse selection); §96b close-entry neutral |
| **6** | **Portfolio-level improvements (HRP, DD throttle, correlation limits)** | +0.05–0.10 Ann.Sharpe | 1 month | **High** | §95 DD throttle already live; §83 correlation penalty already wired |
| **7** | **TCA slippage feedback loop** | Unknown until fills accrue | 3–6 months | **Medium** | Wired but unvalidated; zero fills in ledger |
| **8** | **Universe expansion (150+ tickers)** | +0.10–0.20 Ann.Sharpe if per-trade quality holds | 6–12 months | **Low** | §90 WATCH bench all rejected; 111-name list is already well-filtered |
| **9** | **Free alt-data (FINRA SV, SEC FTD, NAAIM, Wikipedia, GDELT)** | **0.00** — all inside placebo band | — | **N/A** | v8.6–v8.7 retraction stands; no free path deployable |
| **10** | **Meta-model retrain & enable** | +0.02–0.05 Sharpe if CV-AUC crosses 0.52 | 4–6 months | **Medium** | Needs N=400–500 for stable AUC; currently 0.4364 |

### 4.2 Detailed Analysis of Top Opportunities

#### 4.2.1 Cross-Sectional Shadow (h=63) — PROMOTE NOW?

**The case for promotion:**
- Nested-horizon validation: h=63 chosen in **all 12 eval folds (2014–2025)**; selection haircut = 0.000
- Net Sharpe +0.576 [90% CI +0.22, +0.91] — 90% CI excludes zero
- Cost-robust: +0.481 at 40bps one-way (h=21 goes negative at same cost)
- Borrow-robust: +0.572/+0.528 at 50/100bps GC
- Correlation with MR book: +0.03 (genuinely orthogonal)

**The case against immediate promotion:**
- Shadow was silently broken until 2026-06-12 (1y fetch vs 253-bar need → 1y→2y fix)
- Zero forward data accrued since "deployment" on 2026-06-09
- §92 promotion criteria require ≥150 tagged signals, bottom-decile WR ≥3pp worse, monotonic top>bottom, 0.75× haircut — none met yet
- The grid {21,40,63} is not proven optimal; only that 63 beats 21/40

**Recommendation:** Keep in shadow. Begin accrual now (post-2y fix). At ≥150 tagged signals, run the promotion checklist. If criteria met, promote as a **sleeve** (not a replacement) — the MR book and h=63 shadow are uncorrelated and should coexist. Expected portfolio impact: +0.30–0.50 Ann.Sharpe from diversification alone.

#### 4.2.2 Sector-Specific Models

**Current state:** XLF/XLP/XLU/XLI are hard-blocked (live WR 27–37%, −1.2 to −1.8%/trade). §117 infrastructure is complete (promotion gate, ModelRegistry, purged CV, OOS AUC ≥0.55 bar). No model has been trained or promoted.

**Why this matters:** Sector-specific models could unlock 20–30% more trade volume from currently blocked sectors. Financials (XLF) in particular showed 83.3% WR at score≥42 in isolated backtests — the sector block is a blunt instrument killing genuine edge.

**Timeline:**
- Month 1: Train sector models on ≥100 backtest trades per sector
- Month 2: OOS validation, cost-adjusted Sharpe > 0 gate
- Month 3: QENG-1c promotion checklist, live shadow deployment
- Month 4+: If live shadow validates, promote to full delivery

**Risk:** Sector models trained on small N (100 trades over 23 years ≈ 4 trades/year) will have high variance. The OOS AUC ≥0.55 bar is appropriately strict.

#### 4.2.3 Paid Alt-Data: Options Flow, VRP, GEX

**The honest read:** No free alt-data path has cleared the noise floor. The project has self-grown CBOE IV-rank history starting 2026-06-12 (68 tickers, one day). FINRA ATS historical backfill is blocked. SEC FTD, NAAIM, Wikipedia, GDELT all inside placebo.

**Paid options data (ORATS, Unusual Whales, Polygon Options ~$99/mo) is the most plausible next step because:**
- The live engine already has options-flow scaffolding (GEX, put-call skew, IVR, max pain)
- These gates are **unvalidated** (no historical data), which means they could be the missing alpha — or they could be noise
- The only honest way to find out is: buy 6–12 months of historical data, run pre-registered SPRT tests, and measure

**Expected cost:** $150–300/month for 6–12 months = $1,000–3,600 research spend.
**Expected impact:** If options flow adds 0.15 Sharpe, it pays for itself in one month of improved sizing. If it adds nothing, the project has definitively closed the alt-data chapter and can focus on execution/structural improvements.

**Recommendation:** Budget for Unusual Whales or ORATS historical data. Pre-register 2–3 hypotheses in SPRT (e.g., "high call-buying in oversold setups → +5pp WR"). Do not buy without a pre-registered test plan — that is how the free alt-data retraction happened.

#### 4.2.4 Execution Optimization — Mostly Exhausted

| Approach | Result | Verdict |
|---|---|---|
| Close-entry (signal-day fill) | ΔSharpe +0.01, −2.7pp WR | Neutral — convenience, not alpha |
| Limit-order grid (k=0.25/0.5/1.0) | All fail deploy bar (Sh 0.12–0.16) | Adverse selection dominates |
| TCA slippage feedback | Wired but unvalidated | Wait for ≥50 fills |
| Dynamic RSI stops | Embedded in v10.8 baseline | +0.01 Sharpe, already live |

The execution frontier is **not where the edge lives.** The 0.50% friction assumption is already conservative; the gap is alpha generation, not alpha capture.

#### 4.2.5 Portfolio-Level Improvements

| Approach | Status | Impact |
|---|---|---|
| HRP allocator | Live | Baseline risk overlay |
| DD throttle (R7) | Live | Reduces exposure >3% off peak; seq ΔSharpe +0.06, concurrent +0.44 Ann.Sh |
| Correlation penalty (§83) | Live | Cuts avg_corr>0.75 positions by 40% |
| Sector concentration limits | Live | HARD 30%, SOFT 20% |
| L7 score-band sizing | Live | +0.05 Sharpe, zero trade cost |
| L10 conviction sizing | Live | +0.06 Sharpe, ΔN=0 |

Portfolio construction is already well-optimized. Marginal gains here are +0.05–0.10 Sharpe, not transformative.

---

## 5. Signal Quality Roadmap with Milestones

### 5.1 The 3-Month Horizon (Jul–Sep 2026)

**Goal:** Prove the clean post-fix book is reproducible and begin accumulating shadow data.

| Milestone | Target | Go/No-Go Criteria |
|---|---|---|
| **M1. Post-fix N ≥ 150** | 150 resolved BUY signals, all post-2026-06-10 | Go: N≥150; No-Go: N<100 (volume starvation) |
| **M2. Post-fix WR ≥ 55%** | Net-of-friction WR on clean book | Go: WR≥55% with Wilson CI lower bound ≥50%; No-Go: WR<50% |
| **M3. Brier ≤ 0.25** | Calibration skill vs naive 0.25 | Go: Brier≤0.25; No-Go: Brier>0.27 (still broken) |
| **M4. h=63 shadow tagged ≥ 100** | Cross-sectional shadow signals accrued | Go: ≥100 tagged; No-Go: <50 (pipeline broken) |
| **M5. Midday effect validated** | N≥20 in 11–12 ET window | Go: WR≥45% (no longer catastrophic); No-Go: WR<35% (hard filter required) |
| **M6. Sector model trained (1 sector)** | First sector model (XLF most likely) hits ≥100 trades | Go: OOS AUC ≥0.55; No-Go: AUC<0.52 |

**3-Month Expected Sharpe if all GO:** 0.25–0.35 per-trade (clean book + midday filter + sector model shadow).

### 5.2 The 6-Month Horizon (Oct–Dec 2026)

**Goal:** Promote cross-sectional shadow and first sector model; begin paid alt-data SPRT.

| Milestone | Target | Go/No-Go Criteria |
|---|---|---|
| **M7. h=63 shadow promoted** | §92 criteria met | Go: Bottom-decile WR ≥3pp worse, monotonic, ≥150 resolved; No-Go: Criteria not met, keep shadow |
| **M8. Sector model promoted (1 sector)** | First sector unblocked via QENG-1c | Go: Live shadow WR≥55% for sector, N≥50; No-Go: Re-block sector |
| **M9. Paid alt-data SPRT initiated** | Unusual Whales or ORATS data purchased | Go: 2+ hypotheses pre-registered, SPRT monitor live; No-Go: No budget or vendor chosen |
| **M10. Meta-model AUC ≥ 0.52** | Weekly retrain crosses threshold | Go: CV-AUC ≥0.52 with CI lower bound ≥0.50; No-Go: AUC<0.50 (N still too small) |
| **M11. OOS v7/v8 validation** | ≥30 live trades in pre-specified held-out tickers | Go: OOS WR≥50%; No-Go: OOS WR<45% |
| **M12. Calibration v5 (raw_conf)** | Stage mismatch fixed, isotonic-on-isotonic loop broken | Go: Brier≤0.22 on new protocol; No-Go: Brier>0.25 |

**6-Month Expected Sharpe if all GO:** 0.35–0.50 per-trade (MR book + h=63 shadow + 1 sector + meta-model enabled).

### 5.3 The 12-Month Horizon (Jan–Jun 2027)

**Goal:** Achieve consistently investable edge; recommend to friends.

| Milestone | Target | Go/No-Go Criteria |
|---|---|---|
| **M13. 2+ sector models promoted** | XLF + XLY or XLC unblocked | Go: Each sector live shadow WR≥55%, N≥100; No-Go: Keep blocked |
| **M14. Paid alt-data SPRT resolved** | 1+ hypothesis crosses SPRT boundary | Go: SPRT accepts H1 (edge real) at 90% power; No-Go: SPRT accepts H0 (no edge) or inconclusive at 12 months |
| **M15. Full portfolio Ann.Sharpe ≥ 1.0** | Combined MR + shadow + sectors | Go: 12-month rolling portfolio Ann.Sharpe ≥1.0, MaxDD<10%; No-Go: <0.6 |
| **M16. Brier ≤ 0.20** | Well-calibrated confidence | Go: Brier≤0.20, confidence gap ≤5pp; No-Go: >0.22 |
| **M17. Drawdown throttle validated** | R7 DD-throttle proves it helps in live crisis | Go: MaxDD <8% in any 30-day window; No-Go: >12% |
| **M18. Friend-recommendable** | I would recommend this to a risk-tolerant friend | Go: All of M13–M17 GO + 12-month track record + transparent risk docs; No-Go: Any NO-GO |

**12-Month Expected Sharpe if all GO:** 0.50–0.70 per-trade MR book + 0.50–0.60 shadow = **portfolio Ann.Sharpe 1.0–1.5**. This is the threshold where the strategy becomes genuinely attractive to quantitative investors.

### 5.4 What Would Make Me Personally Recommend This?

| Criterion | My Standard | Current Status |
|---|---|---|
| Live WR > 55% (net, 12-month rolling) | Must have | 42.5% (full), 57.8% (post-fix, N=90) |
| Sharpe > 0.50 (per-trade, 12-month) | Must have | 0.24 IS, 0.29 clean live, 0.04 phantom-corrected |
| Brier < 0.20 | Must have | 0.2641 (11pp overconfident) |
| MaxDD < 10% at intended size | Must have | −7.06% concurrent (5 slots) |
| Regime robustness (2+ macro regimes) | Must have | Only VIX 20–30 works; 2022+ epoch negative |
| Transparent risk docs | Must have | Good — RUNBOOK, SIGNAL_VALIDATION, decay monitor |
| Calibration honest | Must have | Stage mismatch open; v4 is directionally okay |
| Auto-execution stable | Nice to have | Alpaca + IBKR wired; gated on WR>55% |
| Independent audit | Nice to have | External quant review (QUANT_ENGINE_REVIEW.md) is excellent |

I would recommend Signal.Trade to a quant-savvy friend with 1–2% risk capital only after **M18 is achieved** — which requires the 12-month track record. I would recommend it to a general retail investor only after **M15 + M18 + independent third-party audit** — the concurrent MaxDD of −7% at 5% position sizing means the strategy is not suitable for investors who cannot tolerate 10%+ drawdowns.

---

## 6. Recommended Position Sizing and Risk Limits for Early Users

### 6.1 Sizing Framework

| User Profile | Capital | Position Size | Max Concurrent | Max Sector Exposure | Max DD Tolerance | Recommended? |
|---|---|---|---|---|---|---|
| **Research / paper only** | Any | 5% per trade | 5 slots | 30% | 10% | **Yes — mandatory** |
| **Small live (<$50K)** | $10K–$50K | 3% per trade | 3 slots | 20% | 5% | **Conditional** — only if WR>55% for 60 days |
| **Medium live ($50K–$250K)** | $50K–$250K | 2% per trade | 4 slots | 20% | 8% | **No** — until M7+M10 achieved |
| **Large live (>$250K)** | >$250K | 1% per trade | 5 slots | 15% | 5% | **No** — until M15 achieved |

### 6.2 Risk Limits

| Risk Control | Setting | Rationale |
|---|---|---|
| **Global kill switch** | Owner-triggered, pauses all auto-execution | Already live; use if WR drops <45% for 30 days |
| **Drawdown circuit-breaker** | Halt at −5% portfolio level (live `_DD_BLOCK_THRESHOLD`) | Tighter than the −7.06% observed concurrent MaxDD |
| **Per-trade stop** | 1.5× ATR (swing) / 1.0× ATR (position) | Backtest-validated sweet spot |
| **Sector hard limit** | 30% portfolio in any sector | Prevents single-sector crash domination |
| **Correlation penalty** | Cut sizing 40% if avg_corr>0.75 | Reduces inventory risk |
| **VIX regime gate** | Suspend new entries if VIX>35 or VIX<15 | Strategy is structurally VIX 20–30 only |
| **Confidence floor** | 40% (BUY), 46% (swing) | Calibrated to net-of-friction breakeven |
| **Broker auto-execute** | **PAPER ONLY** until WR>55% for 100 trades | Per SIGNAL_VALIDATION.md go-live checklist |

### 6.3 The Honest Disclosure

Every user should see this before deploying capital:

> **Expected outcomes:**
> - Best case (12-month, all milestones met): +15–25% annual return, 10–15% MaxDD, Sharpe ~1.0–1.5
> - Base case (current trajectory): +5–10% annual return, 7–10% MaxDD, Sharpe ~0.3–0.5
> - Worst case (regime persists, no improvement): −5–10% annual return, 10–15% MaxDD, Sharpe ~0.0–0.2
> - Tail risk (COVID-style crash): −20–30% in 2–4 weeks, strategy stops firing entirely
>
> **You should NOT use this strategy if:**
> - You cannot tolerate a −10% drawdown
> - You need liquidity within 10 days of entry (hold period is 5–10 days)
> - You are investing retirement funds or cannot afford to lose the capital
> - You expect consistent monthly returns (the strategy fires episodically in stress regimes)

---

## 7. Conclusion

Signal.Trade is a **rare example of honest quant research** in the retail signal space. The team has done something most shops never do: they audited their own delivery leaks, retracted overclaimed alt-data results, published the negative findings, and fixed the meta-model train/serve skew before it caused real harm. The external-lens review (QUANT_ENGINE_REVIEW.md) is a model of intellectual honesty.

**But honesty about problems is not the same as solving them.** The strategy today is a research project with a promising clean book (N=90, 57.8% WR) and a structural ceiling (IS Sharpe 0.24, DSR fails, regime-dependent). It is not yet a product that can responsibly take user capital.

**The path forward is clear and correctly prioritized:**
1. **Accrue post-fix forward data** (priority 0 — everything else waits on this)
2. **Promote h=63 cross-sectional shadow** when §92 criteria met
3. **Train and promote sector-specific models** (XLF first)
4. **Buy paid options data and pre-register SPRT tests**
5. **Fix midday microstructure and calibration stage mismatch**

**The 12-month milestone (M18) is achievable** if the team maintains its current discipline — but it requires patience, capital for data, and a willingness to keep the strategy on paper until the numbers justify live deployment. The strategy that survives that process will be genuinely differentiated. The strategy that rushes to live capital before those milestones is gambling with user trust.

**My final assessment:** Signal.Trade is a **B+ research project** with **A+ intellectual honesty**. The gap between those two grades is what the next 6–12 months must close.

---

*Report prepared by external quantitative researcher.*
*All data sourced from docs/Stats.md, docs/QUANT_ENGINE_REVIEW.md, docs/SIGNAL_VALIDATION.md, docs/LEARNINGS.md, and docs/PROGRESS.md as of 2026-06-15.*
