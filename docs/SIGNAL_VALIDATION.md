# Signal.Trade — Live Engine Signal Validation Status

> Tracks every signal and gate in the live engine (`signal_engine.py`) against its backtest evidence.
> Last updated: **2026-07-14 — gate audit + exit-chronology correction.**
> **2026-07-14 gate audit:** outcomes were re-booked chronologically first (74 both-hit trades had been mislabeled `'target'` with stop-fill P&L — see `validate_predictions.py --fix-exit-chronology`; book +82.5%→+917.8%), then `gate_contribution_analysis.py` + the §85-1 audit ran on the corrected 725-signal book and all-time card-firing counts (87,982 signals) were measured. **Removed:** §64/§65/§66/§68 (macro_extensions module — 0 fires ever), §78 live remnant, min-ATR BUY gate (1 fire ever), §81 (0 fires), §74 Beneish (§85-1: ΔWR −24.2pp @ N=70), §69/§70/§71/§72 stock-score modifiers (untestable + fired 85-95% on blocked SELL/intraday cohorts), §67 FOMC hard block (ΔSh −0.00 + stale date list), §51 forward-PE (24 fires ever), §57 *Friday* HOLD-flip (no ledger entry — the validated §57 *Thursday* threshold is kept). The cohort-EV gate (`services/cohort_edge_gate.py`) is now WIRED into delivery (was dormant) and supersedes the static blocklists over time.
> **2026-06-10 delivery overhaul:** sector model-file unblock removed, SELL delivery disabled, §55/§14 hard blocks removed, DELIV-1 price-validity EOD guard, `skip_reason` persisted — see the 🔴 table + `Stats.md §DELIV`. ⚠ All pre-2026-06-10 live-WR evidence in this doc is contaminated by the delivery leaks (81% null `sector_rs`, unblocked sectors, SELL floor bypass) — and all pre-2026-07-14 live-WR evidence additionally by the exit-chronology mislabeling. Re-validate against the corrected book.
>
> **How to re-run backtest validation:**
> ```bash
> cd backend && python scripts/backtest_technicals.py --validate-live-gates
> ```
> Run after any gate change. Results update the ΔSharpe column below.

---

## Confidence Ontology (2026-06-27)

The signal engine no longer treats every score-like quantity as a single
`confidence` value.  The field is split into explicit roles so that probability,
alpha, sizing, and ranking do not bleed into one another:

| Field | Meaning | Mutated by |
|---|---|---|
| `alphaScore` | Raw composite score before probability mapping. | Scoring families, macro overlays, ML blend. |
| `rawConfidence` | Pre-calibration probability estimate. | Macro overlays, warning deconfliction, hard ceiling. |
| `calibratedProbability` | **Calibrated probability of winning.** | `CalibrationGate` only. |
| `displayConfidence` | User-facing confidence; may include peer/ranking context tilts. | Post-scan peer, Polygon, supply-chain, cross-sectional ranking. |
| `positionSizeScale` | Sizing multiplier for risk, liquidity, correlation, concentration. | Sizing stack, correlation penalty, regime dampeners. |
| `rankScore` / `rankPercentile` | Cross-sectional ordering metadata; never changes probability. | Universe ranking step. |

**Invariant:** `calibratedProbability` is the last probability-mutating step in
`_assemble_signal()` and is never changed by `scan_all()` post-processing.  Any
violation of this invariant is a bug.  The invariant is enforced by
`tests/test_confidence_invariants.py`.

Rule of thumb for future gates:
- **Probability** changes only when evidence changes expected win rate.
- **Sizing** changes when risk, liquidity, correlation, concentration, or portfolio context changes.
- **Ranking** changes only display/order, not probability.

### Ticker performance gate (Stage B, 2026-06-27)

The static defensive-ticker BUY blocklist is being replaced by a point-in-time
`ticker_performance` gate.  It blocks (or size-reduces) a ticker only when the
ticker's own recent resolved signals show a poor decay-weighted win rate with
sufficient sample size (`n >= 5` to block, `n >= 3` to caution).  Auto-retirement
is built in: when forward performance improves, the gate unblocks automatically.

In Stage B the gate runs in **shadow mode** inside `assembler.py`; the legacy
static blocklist still governs delivery.  Both decisions are persisted to
`ticker_perf_shadow_decisions`.  After signals resolve, run
`scripts/analyze_ticker_perf_shadow.py` to compare overlap, forward WR, missed
winners, saved losers, volume impact, sector skew, and outcome-horizon alignment.
After 30 days of shadow logs show parity or improvement, the static list will be
removed and the gate will become the hard block.

The legacy `confidence` key is retained as an alias for `displayConfidence` so
existing consumers continue to work.

## Live Trading Validation Criteria

A gate may be kept in the live engine, but **that does not mean the engine is ready to trade real money**.
The following criteria must be met before broker auto-execute is enabled:

| Criterion | Minimum bar | Evidence source |
|---|---|---|
| Backtest gate validation | All active gates in ✅ or ⚠ tables; no 🔴 gate live | This document |
| Paper track record | ≥ 100 resolved paper trades or ≥ 3 months | `broker_orders` with `account_type='paper'` |
| Clean live win rate | > 55% on delivered BUY signals | `gate_contribution_analysis.py --live` |
| Calibration | Brier ≤ 0.30, confidence gap ≤ 10pp | `backtest_calibration` endpoint |
| Drawdown tolerance | Simulated max DD < 10% at intended size | Simulated Returns panel / `run_portfolio_simulation` |
| Decay monitor | No `"decay"` alarm for 30 days | `scripts/decay_monitor.py` |
| Broker readiness | Live Alpaca/IBKR keys verified, risk acknowledged | `/api/me/broker/status`, `users.risk_acknowledged_at` |

> **Current status:** Live delivery is active and audited; broker auto-execute is implemented but should remain on **paper** until the live win rate is consistently above the 55% bar. See [RUNBOOK.md](RUNBOOK.md) §7 for operational steps.

---

## Summary

| Category | Count | Validated? |
|---|---|---|
| ✅ Backtest-validated (ΔSharpe measured) | 7 | Yes — gate ablation run (§64/§68/§67/§78 removed 2026-07-14) |
| ⚠ Directional evidence only (live data, no backtest) | 4 | Partial — §50 Piotroski re-confirmed +9.3pp on corrected book |
| ❌ Not testable in backtest (look-ahead / paid data) | 10 | No — live-only (§69–§72/§74/§81/§51 removed 2026-07-14) |
| 🔴 Removed / disabled (tested, found harmful or dead) | 17 | Yes — empirical (9 more added by the 2026-07-14 gate audit) |
| ⏳ Monitoring (live tracking, insufficient N to validate) | 1 | No — §93d midday warning, need N≥20 in reliable cohort |
| ➕ Cohort-EV gate (adaptive layer) | 1 | Wired 2026-07-13 — learns per-(action,style,sector) edge from resolved outcomes; supersedes static blocklists over time |
| **Total live engine gates** | **~32 (was 41)** | — |

---

## ✅ Backtest-Validated Gates

Gates where `--validate-live-gates` ablation has produced a measured ΔSharpe.
**Interpretation:** ΔSharpe on REMOVE < −0.02 = gate earns its trade-count cost.

Baseline (v10.8, 2026-06-10): **N=217, WR=69.1%, Sharpe=0.24**

> **§93d gap decomposition update:** Live WR 43.6% vs IS 69.1% = **25.5pp gap**. Primary driver: regime mismatch (live period = 2022+ rate-hike epoch with negative backtest Sharpe). Secondary: midday microstructure (hour 11–12 ET catastrophic, p=0.000). Scanner midday warning added (tracking only, no hard filter yet).

| Gate | Mechanism | In Baseline? | ΔSharpe on Remove | N impact | Verdict |
|---|---|---|---|---|---|
| §57 Thursday strict threshold | score≥55 required for Thu entries | ✅ Yes | **−0.10** | +47 (+21%) | ✅ **KEEP** — largest validated contributor |
| §67 FOMC day hard block | Block BUY on Fed announcement day | ✅ Yes | −0.00 | +4 | ⚠ REVIEW — near-zero N impact |
| §64+§68 T10Y yield curve + rising rates | XLF/XLK sector penalties | ✅ Yes | −0.00 | +1 | ⚠ REVIEW — sector-specific, tiny N |
| §59 OU halflife ≤25d | Block if mean-reversion half-life > 25d | ✅ Yes | −0.00 | +2 | ⚠ REVIEW — not load-bearing at current thresholds |
| §60 Hurst ≤0.80 ceiling | Block if Hurst exponent > 0.80 (trending) | ✅ Yes | +0.00 | +8 | ⚠ REVIEW — adds N, no Sharpe harm or benefit |
| §61 Idiosyncratic vol | Block if realized vol > 55% — **DISABLED** | ✅ Disabled | +0.00 | +0 | 🔴 Confirmed dead — N=0 at threshold |
| §78 Sep floor | score≥55 in Sep — **DISABLED** | ✅ Disabled | +0.00 | +0 | 🔴 Confirmed dead — no trades blocked |
| §78 Oct floor | score≥53 in Oct — **DISABLED** | ✅ Disabled | +0.00 | +0 | 🔴 Confirmed dead — no trades blocked |
| §54 VIX<20 hard block | Block MR BUY when VIX < 20 | ❌ Not in IS | +0.00 ADD | +0 | ⚠ NEUTRAL — currently irrelevant (VIX rarely <20 in this epoch) |
| §47 VIX term structure | VIX/VIX3M < 0.93 + score<60 → block | ❌ Not in IS | **−0.08 ADD** | −50 (−22%) | 🔴 **HURTS** — too aggressive; removes 22% of trades with no WR gain |
| §55 Cross-asset 3/3 headwinds | TLT+UUP+XLE all signalling macro breakdown | ❌ Not in IS | −0.00 ADD | −18 (−8%) | ⚠ NEUTRAL — removes trades but no Sharpe improvement |

**Last run:** 2026-06-02 v10.3 (107 tickers, 2003–2026)

**Re-run command to fill in all ΔSharpe values:**
```bash
cd backend && python scripts/backtest_technicals.py --validate-live-gates 2>&1 | grep -A 40 "Gate Validation"
```

---

## ⚠ Directional Evidence Only (Live Data, No Backtest Possible)

These gates exist in the live engine, produce signals with a rationale card, and have directional evidence from live resolved signals — but cannot be validated in the backtest due to data limitations.

| Gate | Mechanism | Live Evidence | Confidence | Backtest blocker |
|---|---|---|---|---|
| §50 Piotroski F-Score | F≥7→+12, F≥5→+5, F≤4→−4, F≤2→−10 | **EDGAR validated 2026-06-03**. Standalone ΔSh=+0.00 (N 230→228). IS universe already skews healthy (most have F≥2). Keeps its live scoring since it does no harm and adds rationale quality. | ⚠ Neutral — keep |
| §51 Forward PE | PE>30→−5, PE<15→+3 | AQR (Asness 2013) value premium is 12-month, not 10-day | Low | Not point-in-time |
| §52 Short interest velocity | SI down>15%→+4, SI up>20%→−5 | FINRA bi-monthly SI data; squeeze dynamics plausible but N<30 | Medium | FINRA not daily historical |
| §58 EPS revision | Finnhub revision_pts modifier | EPS momentum is 1-4 week effect; directionally correct but unvalidated | Medium | Analyst estimate history not in yfinance |
| §63 Sector cointegration | Cointegration Z<−2.0→+4pts | **Now in backtest** — `coint_z` column computed for every IS ticker. Ablated in `--validate-live-gates`. ΔSharpe pending next run. | Medium→✅ | — |
| §65 TRIN | TRIN>2→capitulation boost; currently metadata only in backtest | TRIN > 2.0 historically associates with MR setups; not yet validated as score gate | Low-Medium | Available as data, but no pre-specified threshold for gate |
| §66 AD breadth | Zweig thrust interaction; currently metadata only | Breadth context available via ^NYAD; gate logic not yet specified for backtest | Low | Available as data, but gate condition not pre-specified |
| §93d Midday warning | Log warning when signal created at 11–12 ET | Live: catastrophic WR 23.7% vs 47.8% baseline (p=0.000, N=97). But May+ reliable cohort shows reversal (N=4, WR=75%). Effect may be regime-specific. | Medium | Backtest uses daily bars; no intraday session modeling |

---

## ❌ Not Testable in Backtest (Look-Ahead Bias or Paid Data)

These gates are in the live engine but **cannot** be added to the backtest without violating point-in-time rules or requiring paid historical data that does not exist in OHLCV.

| Gate | Mechanism | Why untestable | Status |
|---|---|---|---|
| §48 IVR | IVR≥50→+5pp, IVR<20→−3pp | Per-stock options IV rank history not in yfinance | ❌ Unvalidated |
| §49 Put-call skew | 25d skew>0.10→+4pp | Options surface data not historical | ❌ Unvalidated |
| §73 Insider clustering | unique_buyers≥3→+12, sell heavy→−8 | **EDGAR validated 2026-06-03**. Standalone ΔSh=+0.00 (N unchanged at 230). Form 4 raw-count proxy too coarse. Live engine uses `unique_buyers` which is better; keep as-is. | ⚠ Neutral — keep |
| §74 Beneish M-Score | M>−1.78→−8pts (earnings manipulator risk) | Quarterly financials from yfinance not point-in-time; EDGAR alternative possible | ❌ Unvalidated |
| §76 Altman Z-Score | Z<1.81→−10pts (distressed company) | **EDGAR validated — REMOVED 2026-06-03**. 79/106 IS tickers (74%) always below Z'<1.23. Standalone (Z'<1.23): N 230→79, Sh −0.03. Combo §50+§76 showed +0.12 Sh but this was equivalent to BUY_THRESH=55 (Altman false positives acting as threshold filter). **OOS rejected BUY_THRESH=55**: Sh 0.42 IS → 0.00 OOS clean (100% haircut). Recalibrated Z'<0 threshold: all configs ΔSh=0.00. Altman formula designed for 1968 manufacturing — incompatible with tech/financial universe. | 🔴 Removed |
| §62 VRP (deferred) | Per-stock VRP = realized vol vs IV | Polygon Options upgrade required (~$99/mo) | ⏳ Deferred |
| §69 GEX flip | Dealer gamma positioning flip level | Options market maker data; no historical equivalent | ❌ Unvalidated |
| §70 Zero-DTE put spike | 0DTE put open interest surge | Recent phenomenon (2022+); pre-2022 history does not exist | ❌ Unvalidated |
| §71 Max pain | Options max pain convergence | Historical options chain snapshots not in yfinance | ❌ Unvalidated |
| §72 VRP proxy | Realized vol / IV spread | Per-stock IV history not in OHLCV | ❌ Unvalidated |
| §80 NBBO spread | bid-ask >0.5%→−5, >1.0%→−10 | Real-time quote data; no historical bid-ask spread in yfinance | ❌ Unvalidated |
| §81 Block prints | ≥3 block buys→+5pp | Real-time block trade data; no historical equivalent | ❌ Unvalidated |
| §75 Active buyback | Repurchase window scoring | EDGAR 8-K parsing complexity; deferred | ⏳ Deferred |
| §79 Q1 rebalancing | Sector rebalancing seasonal gate | Prior-year sector return at Dec-31 not stored | ⏳ Deferred |
| §84 Survivorship correction | Delisted-ticker inclusion | Norgate/Sharadar point-in-time data required (~$20-33/mo) | ⏳ Deferred |

---

## 🔴 Removed / Disabled Gates (Tested, Found Harmful or Dead)

| Gate | What was tried | Evidence | Outcome |
|---|---|---|---|
| **§64/§65/§66/§68 macro extensions** | TRIN capitulation, Zweig breadth, T10Y yield-curve/rate penalties as confidence modifiers | Gate audit 2026-07-14: **0 fires in 87,982 all-time signals** — ^TRIN/^NYAD 404 (inputs never populate); §64/§68 conditions never triggered; backtest ablation ΔSh −0.00 | **Removed** — `gates/macro_extensions.py` deleted (2026-07-14) |
| **§78 Sep/Oct floors (live remnant)** | conf<62/60 blocks in Sep/Oct in `delivery_gates.py` | Backtest copy removed 2026-06-02 as dead; live copy was left behind | **Removed** from `delivery_gates.py` (2026-07-14) |
| **Min-ATR 0.7% BUY gate** | BUY→HOLD when ATR<0.7% of price | 1 fire in 87,982 all-time signals; claimed "20yr backtest" has no ledger entry; low-ATR defensives covered by cohort-EV + ticker_performance gates | **Removed** from `assembler.py` (2026-07-14) |
| **§81 block prints** | ≥3 block buys→+5 score | 0 fires ever; untestable (no historical block-trade data) | **Removed** from `signal_engine.py` (2026-07-14); `get_recent_block_prints()` kept for research |
| **§74 Beneish M-Score** | M>−1.78→−12 score | §85-1 audit (corrected book): fired N=70, WR 22.9%, **ΔWR −24.2pp** — 24× past removal threshold; fired 0× on surviving BUY position/swing book; not point-in-time | **Removed** from `gates/fundamentals.py` (2026-07-14); `beneish_m` still computed for display |
| **§69/§70/§71/§72 options stock modifiers** | GEX-flip ±5/−2, 0DTE −4, max-pain +4, VRP-proxy +3/−2 score | Untestable (❌ table) + live firing 85–95% on now-blocked SELL/intraday cohorts (WR 11–20% where fired); ~0 fires on surviving book | **Removed** from `options.py` score_options (2026-07-14); fields still computed; options_vrp engine unaffected |
| **§67 FOMC hard block + −4pp haircut** | Block BUY on FOMC day; −4pp day before | Ablation ΔSh −0.00 (+4 N); hardcoded `_FOMC_DATES` list was rotting (unit test already failing) | **Removed** from `delivery_gates.py` (2026-07-14) |
| **§51 Forward-PE trap** | PE>30→−5, PE<15→+3 | 24 fires in 87,982 (cheap side: 0), N<3 resolved; "Low" ledger confidence (12-month value premium ≠ 10d MR) | **Removed** from `gates/fundamentals.py` (2026-07-14) |
| **§57 Friday HOLD-flip** | BUY→HOLD Friday when score<65 | Claimed "20yr backtest ~0.40%" — **no ledger entry**; only the Thursday threshold was ablated (that one KEEPS, ΔSh −0.10) | **Removed** from `gates/calendar.py` (2026-07-14) |
| **§48 IvrMrGate / §49 PutCallSkewGate / IvTermStructureGate** | ±3–5 score MR credits on IVR/skew/IV-term-spike | Gate audit round 2 (2026-07-14): **exact-head search = 0 fires in 87,982 all-time signals** — the opt_flow+has_mr(+VIX>15) precondition combo is never satisfied at assembler stage; the credits never applied once | **Removed** from `gates/options.py` + assembler pipeline (2026-07-14) |
| **'Inverted Skew' +5 score boost** | skew_25d < −0.05 → +5 in score_options | Live: N=70 delivered go-forward, **ΔWR −4.0pp**; no citation. Put-skew −4 penalty KEPT (fired cohort correctly underperforms) | **Removed** from `options.py` (2026-07-14) |
| **Risk-free-rate yield dampener** | −14/−pp/+5pp confidence vs T10Y hurdle | Fired on **76% of delivered book** (N=323) at ΔWR +0.7pp — universal no-op, arbitrary constants (3.5/2.0pp premiums), no ledger entry | **Removed** from `assembler.py` (2026-07-14); §14 FRED dampener carries rate context |
| **§77 −4pp penalty (too weak)** | Near 52-wk low → −4pp | Corrected-book audit: penalized cohort **still ΔWR −16.4pp, negative net EV** (N=21) | **Strengthened to hard block** (BUY→HOLD) in `gates/calendar.py` (2026-07-14) |
| **Sector model-file dynamic unblock** | BLOCKED_SECTORS lifted when `backtest_ml_model_{SECTOR}.json` exists (v8.1 feature 2f0cdcd) | **The biggest live leak found to date (2026-06-10):** files existed for XLF/XLI/XLP → only XLU actually enforced. 60d delivered BUYs: XLF 72 @ 29.2% net WR (−1.52%/trade), XLP 50 @ 24.0% (−1.22%), XLI 35 @ 37.1% (−1.27%) = 32% of book at ≈−1.4%/trade. Training artifacts flipped delivery policy with no promotion gate. | **Removed** from `delivery_gates.py` (2026-06-10); 6 files quarantined to `data/quarantine/`; unblock now requires QENG-1c promotion record |
| **SELL delivery** | SELL signals delivered live (backtest §32 had disabled them: Sharpe 0.20→−0.03) | 60d live: 71 resolved SELLs, net WR 35.2%, **−1.00%/trade**; some sent at conf 35 — below min_confidence=40 and swing floor 46 (gate bypass on a SELL path) | **Disabled** in `delivery_gates.py` (2026-06-10) — long-only regime until a SELL-specific validated path exists |
| §55 Cross-asset 3/3 headwinds hard block | Hard block when TLT+UUP+XLE all stressed | `--validate-live-gates`: −18 trades (−8%) for −0.00 ΔSharpe — pure N destruction | **Removed** from `delivery_gates.py` (2026-06-10); soft −10 scoring in `macro.py` preserved |
| §14 FRED panel hard blocks | NFCI>0.5 / Baa-10Y>4% hard blocks + score<50/55 marginal blocks | Original read +0.02 Sh (marginal, "not a live gate yet") but deployed anyway; **fresh v10.9 canon A/B: −0.06 Sharpe, WR −2.0pp — harmful** ("regime gates cut too many recoverable dips") | **Removed** from `delivery_gates.py` (2026-06-10); soft scoring preserved |
| EOD 120-min stale cutoff | Skip EOD-batch signals older than 2h (interim Item 2, lived <1 day) | Latency was confounded with sector: clean-sector stale deliveries earn **+2.12%/trade** (N=91) vs fresh +3.61% (N=20); cutoff would drop ~82% of clean deliverable trades — the ATR≤70 trap on the delivery side. Also had a latent aware-vs-naive datetime TypeError | **Replaced** (2026-06-10) by DELIV-1 price-validity guard: skip iff price ≥ entry+0.5×ATR or ≤ stop |
| §75 Buyback boost | Score boost during active repurchase window | Live WR 33.8%, −8.7pp drag vs no-buyback | **Disabled** — live engine `signal_engine.py` |
| §77 Tax-loss boost | +4pp Nov/Dec near 52-wk low | Live WR 31% near 52-wk low (INVERTED vs theory) | **Inverted to −4pp penalty** |
| §61 Idio vol gate | Block when realized vol > threshold | `--inv5`: +3N, +0.01Sh → dead gate. Backtest + live engine (`gates/statistical.py`) | **Removed** (2026-06-02) |
| §78 Sep/Oct floor | Score floor 55/53 in Sep/Oct | `--inv5`: +11N, −0.01Sh → dead at 100-ticker scale | **Removed** (2026-06-02) |
| L9 bear dampener | Size down in HMM bear regime | Bear regime WR=72% > baseline WR — was cutting the best setups | **Removed** from `positionSizeScale` |
| §76 Altman Z-Score | Z<1.81→−15pts, grey zone −4pts | EDGAR point-in-time validation: 74% of IS tickers always below Z'<1.23 — structural false positives (financial sector leverage, tech goodwill). Standalone: Sh 0.20→0.16 (−0.03). Apparent +0.12 Sh in combo was BUY_THRESH=55 equivalent. | **Removed** from `gates/fundamentals.py` (2026-06-03) |
| ATR≤70 live gate | Block entries when ATR%rank > 70 | IS: +0.05 Sh but N drops 50% → ann. Sh FALLS 0.95→0.78 (N reduction dominates) | **Research-only** — never deployed live |

---

## §85-1 Audit — Fundamental Modifiers (RAN 2026-07-14 on corrected book)

The live engine applies fundamental modifiers that do NOT exist in the IS backtest.
**Ran on the exit-chronology-corrected 725-signal book** (baseline WR 47.0%):

**Script:** `python scripts/gate_contribution_analysis.py --section85`

**Threshold for removal:** ΔWR < −1pp with N ≥ 30 resolved signals.

| Gate | Result (2026-07-14) | Verdict |
|---|---|---|
| §50 Piotroski | N=165, WR 56.4%, **ΔWR +9.3pp** | ✅ KEEP |
| §52 SI velocity | N=7, WR 85.7%, ΔWR +38.7pp | ✅ KEEP (thin N — keep watching) |
| §74 Beneish M-Score | N=70, WR 22.9%, **ΔWR −24.2pp** | ❌ **REMOVED 2026-07-14** (fired 0× on surviving BUY position/swing book) |
| §51 Forward PE | N<3 fired (24 all-time, cheap-side 0) | ❌ **REMOVED 2026-07-14** (inert + no horizon fit) |
| §58 EPS revision | N<3 fired | ⏳ inert — candidate for later simplification |
| §73 Insider clustering | N<3 in audit patterns | ⚠ EDGAR-validated neutral — keep as-is |
| §76 Altman Z-Score | — | 🔴 already removed 2026-06-03 |

**Confound caveat:** §74's drag concentrated on the now-blocked SELL/intraday cohorts; within the go-forward BUY position/swing cohort (N=473, baseline 54.1%) the strong positives hold: §60 Hurst quality card +13.4pp (N=37), §50 Piotroski +8.5pp (N=107).

---

## How to Keep This Doc Current

1. After any gate change, re-run `--validate-live-gates` and update the ΔSharpe cells.
2. After §85-1 audit runs (≥200 resolved signals), fill in the §50/§51/§52/§73/§74/§76 rows.
3. When a ❌ gate gets validated via live data, promote it to ✅ or ⚠.
4. When a gate is removed, move it to the 🔴 table with the evidence.

```bash
# Full validation refresh
cd backend && python scripts/backtest_technicals.py --validate-live-gates 2>&1 | tee /tmp/gate_validation.txt
python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01
```
