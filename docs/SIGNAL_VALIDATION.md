# Signal.Trade — Live Engine Signal Validation Status

> Tracks every signal and gate in the live engine (`signal_engine.py`) against its backtest evidence.
> Last updated: 2026-06-10 evening — v10.9 IS canon (N=217, WR=69.1%, Sharpe=0.24; DSR ⚠ fails at honest 744 trials) + live delivery overhaul.
> **2026-06-10 delivery overhaul:** sector model-file unblock removed, SELL delivery disabled, §55/§14 hard blocks removed, DELIV-1 price-validity EOD guard, `skip_reason` persisted — see the 🔴 table + `Stats.md §DELIV`. ⚠ All pre-2026-06-10 live-WR evidence in this doc is contaminated by the delivery leaks (81% null `sector_rs`, unblocked sectors, SELL floor bypass) — re-validate findings against the post-fix forward window.
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
| ✅ Backtest-validated (ΔSharpe measured) | 11 | Yes — gate ablation run (§63 cointegration added 2026-06-03) |
| ⚠ Directional evidence only (live data, no backtest) | 5 | Partial — live WR observed (§50/§73 EDGAR: confirmed neutral) |
| ❌ Not testable in backtest (look-ahead / paid data) | 17 | No — live-only |
| 🔴 Removed / disabled (tested, found harmful or dead) | 8 | Yes — empirical (§76 Altman added 2026-06-03) |
| ⏳ Monitoring (live tracking, insufficient N to validate) | 1 | No — §93d midday warning, need N≥20 in reliable cohort |
| **Total live engine gates** | **41** | — |

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

## §85-1 Audit — Fundamental Modifiers (Pending ≥200 Resolved Signals)

The live engine applies fundamental modifiers (§50/§51/§52/§58/§73/§74/§76) that do NOT exist in the IS backtest. The IS/live WR gap is **25.7pp** (IS 68.2% → live 42.5%). Some fraction of this gap is caused by misfiring fundamental gates.

**Script:** `python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01`

**Threshold for removal:** ΔWR < −1pp with N ≥ 30 resolved signals.

| Gate | Pre-audit status | Expected horizon fit |
|---|---|---|
| §50 Piotroski | Scores applied; A19 fix removed double-count | Low — annual metric on 10d trade |
| §51 Forward PE | −5pp if PE>30; +3pp if PE<15 | Low — valuation multiples don't predict 10d bounce |
| §52 SI velocity | +4/−5 modifier | Medium — short squeeze can compress into 10d |
| §58 EPS revision | revision_pts multiplier | Medium — analyst revision momentum 1-4wk |
| §73 Insider clustering | unique buyers bonus | Low-medium — EDGAR filings lag by 48h+ |
| §74 Beneish M-Score | −8pp if manipulator signal | Low — accounting quality irrelevant to MR bounce |
| §76 Altman Z-Score | −10pp if distressed | Low — distress is multi-quarter, not 10d |

**Run §85-1 audit once ≥200 resolved signals are available. Disable any modifier with ΔWR < −1pp and N ≥ 30.**

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
